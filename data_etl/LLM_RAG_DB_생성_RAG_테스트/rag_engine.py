# rag_engine.py
import json
from neo4j import GraphDatabase
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from google import genai
import config

class RAGEngine:
    def __init__(self):
        """엔진 초기화 및 클라이언트 연결"""
        self.neo4j_driver = GraphDatabase.driver(config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD))
        self.qdrant_client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
        
        genai.configure(api_key=config.GOOGLE_API_KEY)
        self.llm = genai.GenerativeModel(config.GENERATION_MODEL_NAME)
        print("RAG 엔진이 초기화되었습니다.")

    def close(self):
        """데이터베이스 연결 종료"""
        self.neo4j_driver.close()

    def _decompose_query(self, query: str) -> dict:
        """LLM을 사용하여 쿼리를 엔티티와 시맨틱 쿼리로 분해합니다."""
        prompt = f"""
        사용자 질문을 분석하여 JSON 형식으로 엔티티와 시맨틱 쿼리를 추출해줘.
        엔티티 타입은 'game', 'developer', 'publisher', 'genre', 'category' 중 하나여야 해.
        
        질문: "Wild Rooster가 배급한 픽셀 그래픽 인디 게임이 있나요?"
        출력:
        {{
            "entities":,
            "semantic_query": "픽셀 아트 스타일의 인디 게임"
        }}

        질문: "Galactic Bowling과 비슷한 볼링 게임 추천해줘."
        출력:
        {{
            "entities":,
            "semantic_query": "은하계를 배경으로 한 재미있는 볼링 게임"
        }}

        질문: "{query}"
        출력:
        """
        try:
            response = self.llm.generate_content(prompt)
            # Gemini 응답에서 JSON 부분만 추출
            json_str = response.text.strip().split('```json\n')[-1].split('```')
            return json.loads(json_str)
        except (json.JSONDecodeError, IndexError, Exception) as e:
            print(f"쿼리 분해 중 오류 발생: {e}. 시맨틱 검색만 진행합니다.")
            return {"entities": [], "semantic_query": query}

    def _hybrid_retrieval(self, decomposed_query: dict) -> list:
        """Qdrant로 후보군을 찾고 Neo4j로 필터링 및 강화합니다."""
        semantic_query = decomposed_query.get("semantic_query")
        entities = decomposed_query.get("entities", [])

        # 1. Qdrant 벡터 검색 (후보군 생성)
        query_vector = self.embedding_model.encode(semantic_query).tolist()
        search_results = self.qdrant_client.search(
            collection_name=config.QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            limit=20  # 초기 후보군 수
        )
        candidate_appids = [hit.payload['appid'] for hit in search_results]

        if not candidate_appids:
            return

        # 2. Neo4j 그래프 강화 (필터링 및 컨텍스트 확장)
        with self.neo4j_driver.session() as session:
            match_clauses = []
            params = {"appids": candidate_appids}
            
            for i, entity in enumerate(entities):
                etype, evalue = entity.get("type"), entity.get("value")
                if etype and evalue:
                    node_label = etype.capitalize()
                    param_name = f"value{i}"
                    if node_label == "Game":
                         match_clauses.append(f"MATCH (g)--(:{node_label} {{name: ${param_name}}})")
                    else:
                        match_clauses.append(f"MATCH (g)-->(:{node_label} {{name: ${param_name}}})")
                    params[param_name] = evalue

            # 컨텍스트를 풍부하게 하기 위해 관련된 모든 정보를 가져옴
            return_clause = """
            RETURN g.appid AS appid, g.name AS name, g.about AS about,
                   COLLECT(DISTINCT d.name) AS developers,
                   COLLECT(DISTINCT p.name) AS publishers,
                   COLLECT(DISTINCT gn.name) AS genres,
            LIMIT 5
            """
            
            full_query = (
                "\n".join(match_clauses) +
                "\nOPTIONAL MATCH (g)-->(d:Developer)"
                "\nOPTIONAL MATCH (g)-->(p:Publisher)"
                "\nOPTIONAL MATCH (g)-->(gn:Genre)"
                f"\n{return_clause}"
            )
            
            results = session.run(full_query, params)
            return [record.data() for record in results]

    def _synthesize_context(self, retrieved_data: list) -> str:
        """검색된 데이터를 LLM이 이해하기 쉬운 형식으로 변환합니다."""
        if not retrieved_data:
            return "관련 정보를 찾을 수 없었습니다."

        context_str = "--- 검색된 정보 ---\n\n"
        for item in retrieved_data:
            context_str += f"게임명: {item.get('name', 'N/A')} (AppID: {item.get('appid', 'N/A')})\n"
            context_str += f"  - 설명: {item.get('about', 'N/A')[:300]}...\n"
            context_str += f"  - 개발사: {', '.join(item.get('developers', []))}\n"
            context_str += f"  - 배급사: {', '.join(item.get('publishers', []))}\n"
            context_str += f"  - 장르: {', '.join(item.get('genres', []))}\n"
        
        return context_str

    def query(self, user_query: str) -> str:
        """전체 RAG 파이프라인을 실행합니다."""
        print("1. 쿼리 분해 중...")
        decomposed = self._decompose_query(user_query)
        print(f"   - 분해 결과: {decomposed}")

        print("2. 하이브리드 검색 실행 중...")
        retrieved = self._hybrid_retrieval(decomposed)

        print("3. 컨텍스트 종합 중...")
        context = self._synthesize_context(retrieved)

        print("4. 최종 답변 생성 중...")
        final_prompt = f"""
        당신은 Steam 게임 전문가입니다. 아래에 제공된 '검색된 정보'에만 근거하여 사용자의 질문에 답변하세요.
        정보에 없는 내용은 언급하지 말고, 추측하지 마세요.

        {context}

        --- 사용자 질문 ---
        {user_query}

        --- 답변 ---
        """
        
        response = self.llm.generate_content(final_prompt)
        return response.text