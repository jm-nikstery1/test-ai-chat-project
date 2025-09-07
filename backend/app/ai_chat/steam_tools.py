# steam_tools.py
from . import config
import google.generativeai as genai
from sqlalchemy import create_engine, text
from neo4j import GraphDatabase
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import torch
import re
import json

class SteamToolbelt:
    """
    MySQL(Text-to-SQL) 및 LightRAG(Qdrant+Neo4j) 쿼리를 실행하는 도구 모음입니다.
    """
    def __init__(self):
        self.llm = genai.GenerativeModel(config.GEMINI_MODEL_NAME)
        db_uri = f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
        self.db_engine = create_engine(db_uri)
        self.neo4j_driver = GraphDatabase.driver(config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD))
        self.qdrant_client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL_NAME, device=device)
        print(f"모든 도구가 성공적으로 초기화되었습니다. (Embedding Device: {device})")

    def _create_final_sql_answer(self, original_query: str, db_result: list) -> str:
        """DB 결과를 바탕으로 LLM을 통해 자연스러운 최종 답변을 생성합니다."""
        if not db_result:
            return "해당 조건에 맞는 데이터를 찾을 수 없습니다."
        
        result_str = "\n".join([str(row) for row in db_result])

        # --- [핵심 수정] LLM이 다른 질문을 하지 못하도록 프롬프트를 매우 명확하고 강력하게 변경 ---
        prompt = f"""
        당신의 유일한 임무는 주어진 데이터베이스 결과를 바탕으로 사용자의 질문에 대한 사실 기반의 답변을 '완전한 문장'으로 만드는 것입니다.
        절대로 사용자에게 질문을 되묻거나 추가 정보를 요청하지 마세요. 오직 주어진 결과로만 답변을 완성하세요.

        - 사용자의 질문: "{original_query}"
        - 데이터베이스 결과:
        {result_str}

        - 엄격한 규칙:
          1. 답변은 항상 완전한 문장 형태여야 합니다.
          2. 데이터베이스 결과를 그대로 사용하여 사실만을 전달해야 합니다.
          3. "알겠습니다" 또는 "결과를 알려드릴게요" 같은 서론을 붙이지 마세요.

        - 예시:
          - (질문: "Linux 지원 게임 수", 결과: "(13686,)") -> "스팀에서 Linux를 지원하는 게임은 총 13,686개입니다."
          - (질문: "가장 비싼 게임", 결과: "('Gray Zone Warfare', 250.0)") -> "현재 스팀에서 가장 비싼 게임은 'Gray Zone Warfare'이며, 가격은 250.0달러입니다."

        이제 위의 규칙을 반드시 지켜서 최종 답변을 생성하세요:
        """
        try:
            response = self.llm.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"답변 생성 중 오류 발생: {e}\n원본 데이터: {result_str}"

    def query_structured_data(self, query: str) -> str:
        """사용자의 질문을 SQL로 변환, 실행하고, 그 결과를 자연스러운 문장으로 변환합니다."""
        prompt = f"""
        당신은 MySQL 전문가입니다. 사용자의 질문을 `{config.STRUCTURED_TABLE_NAME}` 테이블에 대한 단일 SQL 쿼리로 변환하세요.
        - 테이블 스키마 정보: 이 테이블은 appid, name, peak_ccu, required_age, price, windows, mac, linux, metacritic_score, positive, negative, achievements, recommendations, average_playtime_forever 등의 컬럼을 포함합니다.
        - 주의: 응답은 오직 실행 가능한 SQL 쿼리문 하나만 포함해야 합니다. 다른 설명이나 Markdown 형식(```sql)을 절대 추가하지 마세요.

        질문: "{query}"
        SQL 쿼리:
        """
        try:
            print("   1. LLM으로 Text-to-SQL 변환 중...")
            response = self.llm.generate_content(prompt)
            sql_query = response.text.strip()
            
            match = re.search(r"```sql\n(.*?)\n```", sql_query, re.DOTALL)
            clean_sql = match.group(1).strip() if match else sql_query.replace("`", "").strip()
            if not clean_sql.endswith(';'):
                clean_sql += ';'
            
            print(f"   2. 정제된 SQL 쿼리: {clean_sql}")

            with self.db_engine.connect() as connection:
                print("   3. 데이터베이스에 쿼리 실행 중...")
                result = connection.execute(text(clean_sql))
                rows = result.fetchall()
                print("   4. 쿼리 실행 완료. 이제 자연어 답변을 생성합니다...")
            
            return self._create_final_sql_answer(query, rows)

        except Exception as e:
            return f"Text-to-SQL 처리 중 오류 발생: {e}"

    def query_unstructured_data(self, query: str) -> str:
        """LightRAG 파이프라인을 실행하여 비정형 데이터를 조회합니다."""
        try:
            print("   1. LightRAG: 쿼리 분해 중...")
            decomposed_str = self._decompose_query_for_rag(query)
            
            decomposed_json = {}
            try:
                json_match = re.search(r"\{.*\}", decomposed_str, re.DOTALL)
                if not json_match:
                    raise json.JSONDecodeError("No JSON object found", decomposed_str, 0)
                decomposed_json = json.loads(json_match.group())
            except json.JSONDecodeError:
                print(f"   [경고] 쿼리 분해 실패. 원본 쿼리를 시맨틱 검색에 사용합니다.")
                decomposed_json = {'entities': [], 'semantic_query': query}

            print(f"   2. LightRAG: 분해 결과: {decomposed_json}")
            
            print("   3. LightRAG: 하이브리드 검색 실행 중...")
            retrieved_data = self._hybrid_retrieval(decomposed_json)
            if not retrieved_data:
                return "관련된 게임 정보를 찾을 수 없었습니다."
            
            print("   4. LightRAG: 검색된 정보로 최종 답변 생성 중...")
            for game in retrieved_data:
                game['about'] = game.get('about', '설명 정보 없음')
            
            final_answer = self._generate_final_answer(query, retrieved_data)
            return final_answer

        except Exception as e:
            return f"LightRAG 처리 중 오류 발생: {e}"
            
    def _decompose_query_for_rag(self, query: str) -> str:
        prompt = f"""
        사용자 질문을 분석하여 JSON 형식으로 핵심 엔티티와 검색 의도를 추출해줘.
        - 'entities'는 게임 이름, 개발사, 배급사, 장르, 태그 등을 포함할 수 있어.
        - 'semantic_query'는 전체 질문의 핵심적인 의미를 담고 있는 검색용 문장이야.
        - 주의: 다른 설명 없이 오직 JSON 객체 하나만 응답해야 해. 예시: {{"entities": [{{"type": "developer", "name": "FromSoftware"}}], "semantic_query": "FromSoftware가 만든 소울라이크 게임"}}

        질문: "{query}"
        JSON:
        """
        response = self.llm.generate_content(prompt)
        return response.text

    def _hybrid_retrieval(self, decomposed_json: dict) -> list:
        semantic_query = decomposed_json.get('semantic_query', '')
        query_vector = self.embedding_model.encode(semantic_query).tolist()
        qdrant_hits = self.qdrant_client.search(
            collection_name=config.QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            limit=5
        )
        
        retrieved_games = {hit.payload['appid']: hit.payload for hit in qdrant_hits}
        return list(retrieved_games.values())

    def _generate_final_answer(self, query: str, retrieved_data: list) -> str:
        context = "--- 참고 정보 ---\n"
        for game in retrieved_data:
            context += f"- 게임명: {game.get('name', 'N/A')}\n"
            context += f"  - 설명: {game.get('about', '정보 없음')[:200]}...\n"
        
        prompt = f"""
        당신은 친절한 게임 전문가입니다. 주어진 참고 정보를 바탕으로 사용자의 질문에 답변해주세요.
        참고 정보에 없는 내용은 언급하지 마세요.

        {context}

        사용자 질문: "{query}"
        답변:
        """
        response = self.llm.generate_content(prompt)
        return response.text.strip()

    def close(self):
        if self.neo4j_driver:
            self.neo4j_driver.close()
        print("DB 연결이 모두 종료되었습니다.")

