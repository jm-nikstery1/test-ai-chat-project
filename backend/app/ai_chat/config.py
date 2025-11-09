# config.py
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
# 이 스크립트가 실행되는 위치에 .env 파일이 있어야 합니다.
load_dotenv()

# --- API 및 모델 설정 ---
# Google Gemini API 키
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("'.env' 파일에 GOOGLE_API_KEY가 설정되지 않았습니다.")

# LLM 모델 (에이전트 라우팅, RAG 답변 생성, Text-to-SQL 변환 등 모든 작업에 사용)
GEMINI_MODEL_NAME = "gemini-2.0-flash"

# 로컬 임베딩 모델 (Qdrant 벡터 생성을 위해 사용)
#EMBEDDING_MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# --- MySQL 데이터베이스 설정 (Text-to-SQL용) ---
DB_USER = os.getenv("DB_USER", "test1")
DB_PASSWORD = os.getenv("DB_PASSWORD", "test1")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "steam_structured_db")
# Text-to-SQL 쿼리의 대상이 될 테이블 이름
STRUCTURED_TABLE_NAME = "steam_structured_data"


# --- Qdrant 벡터 데이터베이스 설정 (RAG - 의미 검색용) ---
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_COLLECTION_NAME = "steam_games"


# --- Neo4j 그래프 데이터베이스 설정 (RAG - 관계 검색용) ---
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "test1")
# .env 파일에 설정된 Neo4j 비밀번호를 불러옵니다.
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "rootroot")

