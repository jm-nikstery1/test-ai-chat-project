# config.py
import os
from dotenv import load_dotenv

#.env 파일에서 환경 변수 로드
load_dotenv()

# --- API 및 모델 설정 ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY가.env 파일에 설정되지 않았습니다.")

# 로컬 임베딩 모델
#EMBEDDING_MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)
# RAG 답변 생성을 위한 Gemini 모델
GENERATION_MODEL_NAME = "gemini-2.0-flash"

# --- 데이터베이스 설정 ---
# Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Qdrant
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_COLLECTION_NAME = "steam_games"

# --- 파일 경로 ---
# 데이터를 불러올 JSON 파일의 경로를 지정합니다.
JSON_DATA_PATH = "steam_games_unstructured_data.json"