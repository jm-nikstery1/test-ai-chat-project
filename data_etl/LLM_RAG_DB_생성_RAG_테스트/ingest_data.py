# ingest_data_from_json.py
import json
from neo4j import GraphDatabase
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import config
import torch

# --- 데이터 처리 함수 ---

def load_data_from_json(filepath):
    """지정된 경로에서 JSON 파일을 로드합니다."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"'{filepath}'에서 {len(data)}개의 게임 데이터를 성공적으로 로드했습니다.")
        return data
    except FileNotFoundError:
        print(f"오류: '{filepath}' 파일을 찾을 수 없습니다.")
        return None
    except json.JSONDecodeError:
        print(f"오류: '{filepath}' 파일이 올바른 JSON 형식이 아닙니다.")
        return None

def split_string_to_list(value):
    """
    입력값이 문자열이면 쉼표로 분리하여 리스트로 만들고,
    이미 리스트이면 그대로 반환합니다.
    """
    if isinstance(value, str):
        return [item.strip() for item in value.split(',') if item.strip()]
    elif isinstance(value, list):
        return value
    return []

# --- Neo4j 데이터 저장 함수 ---

def populate_neo4j(driver, game_data):
    """게임 데이터를 Neo4j 데이터베이스에 저장합니다."""
    print("Neo4j에 데이터 저장을 시작합니다...")
    with driver.session() as session:
        # 기존 데이터 삭제 (중복 방지)
        session.run("MATCH (n) DETACH DELETE n")
        print("Neo4j의 기존 데이터를 삭제했습니다.")

        for game in tqdm(game_data, desc="Neo4j 데이터 저장 중"):
            # Game 노드 생성 또는 업데이트
            session.run("""
                MERGE (g:Game {appid: $appid})
                ON CREATE SET g.name = $name, g.release_date = $release_date
                ON MATCH SET g.name = $name, g.release_date = $release_date
            """, appid=game.get('appid'), name=game.get('name'), release_date=game.get('release_date'))

            # Developer, Publisher, Genre, Category 노드 및 관계 생성
            for dev in split_string_to_list(game.get('developers', [])):
                session.run("""
                    MERGE (d:Developer {name: $dev_name})
                    WITH d
                    MATCH (g:Game {appid: $appid})
                    MERGE (d)-[:DEVELOPED]->(g)
                """, dev_name=dev, appid=game.get('appid'))

            for pub in split_string_to_list(game.get('publishers', [])):
                session.run("""
                    MERGE (p:Publisher {name: $pub_name})
                    WITH p
                    MATCH (g:Game {appid: $appid})
                    MERGE (p)-[:PUBLISHED]->(g)
                """, pub_name=pub, appid=game.get('appid'))
            
            for genre in split_string_to_list(game.get('genres', [])):
                session.run("""
                    MERGE (gn:Genre {name: $genre_name})
                    WITH gn
                    MATCH (g:Game {appid: $appid})
                    MERGE (g)-[:HAS_GENRE]->(gn)
                """, genre_name=genre, appid=game.get('appid'))

            for cat in split_string_to_list(game.get('categories', [])):
                session.run("""
                    MERGE (c:Category {name: $cat_name})
                    WITH c
                    MATCH (g:Game {appid: $appid})
                    MERGE (g)-[:HAS_CATEGORY]->(c)
                """, cat_name=cat, appid=game.get('appid'))

    print("Neo4j 데이터 저장을 완료했습니다.")

# --- Qdrant 데이터 저장 함수 ---

def populate_qdrant(client, embedding_model, game_data):
    """게임 데이터를 임베딩하여 Qdrant에 저장합니다."""
    print("Qdrant에 데이터 저장을 시작합니다...")
    
    # Qdrant 컬렉션 재생성 (기존 데이터 삭제)
    try:
        client.recreate_collection(
            collection_name=config.QDRANT_COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=embedding_model.get_sentence_embedding_dimension(),
                distance=models.Distance.COSINE
            )
        )
        print(f"Qdrant 컬렉션 '{config.QDRANT_COLLECTION_NAME}'을(를) 새로 생성했습니다.")
    except Exception as e:
        print(f"Qdrant 컬렉션 생성 중 오류 발생: {e}")
        return

    points_to_upsert = []
    for game in tqdm(game_data, desc="Qdrant 데이터 임베딩 및 준비 중"):
        # 의미 검색을 위한 텍스트 구성
        semantic_text = (
            f"Game: {game.get('name', '')}. "
            f"Genres: {', '.join(split_string_to_list(game.get('genres', [])))}. "
            f"About: {game.get('about_the_game', '')}"
        )
        
        vector = embedding_model.encode(semantic_text).tolist()
        
        # payload에는 검색 결과로 보여주고 싶은 주요 정보만 담습니다.
        payload = {
            "appid": int(game['appid']),
            "name": game.get('name', ''),
            "genres": split_string_to_list(game.get('genres', [])),
            "about": game.get('about_the_game', '')[:500] + '...' # 설명은 일부만 저장
        }

        points_to_upsert.append(
            models.PointStruct(
                id=int(game['appid']),
                vector=vector,
                payload=payload
            )
        )

    # 데이터를 Qdrant에 일괄 업로드
    client.upsert(
        collection_name=config.QDRANT_COLLECTION_NAME,
        points=points_to_upsert,
        wait=True
    )
    print("Qdrant 데이터 저장을 완료했습니다.")


# --- 메인 실행 로직 ---
if __name__ == "__main__":
    game_data = load_data_from_json(config.JSON_DATA_PATH)
    
    if game_data:
        # --- Neo4j 연결 및 데이터 저장 ---
        try:
            neo4j_driver = GraphDatabase.driver(config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD))
            populate_neo4j(neo4j_driver, game_data)
            neo4j_driver.close()
        except Exception as e:
            print(f"Neo4j 연결 또는 데이터 저장 중 오류 발생: {e}")

        # --- Qdrant 연결 및 임베딩 모델 로드 ---
        try:
            qdrant_client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"사용할 디바이스: {device}")
            embedding_model = SentenceTransformer(config.EMBEDDING_MODEL_NAME, device=device)
            
            populate_qdrant(qdrant_client, embedding_model, game_data)
        except Exception as e:
            print(f"Qdrant 연결 또는 데이터 저장 중 오류 발생: {e}")
