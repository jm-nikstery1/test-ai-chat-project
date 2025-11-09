# LLM Chat Application

Open WebUI나 LibreChat과 같은 LLM 채팅 사이트를 FastAPI 백엔드와 TypeScript 프론트엔드로 구현한 프로젝트입니다.
- 사용데이터 - https://www.kaggle.com/datasets/fronkongames/steam-games-dataset/data

## 주요 기능

- **사용자 인증**: JWT 기반 로그인/회원가입
- **채팅 관리**: 채팅 생성, 삭제, 메시지 저장
- **실시간 채팅**: 메시지 전송 및 응답
- **반응형 UI**: 모던하고 직관적인 사용자 인터페이스
- **데이터베이스**: SQLite/PostgreSQL 지원

## 기술 스택

### 백엔드

- **FastAPI**: 고성능 Python 웹 프레임워크
- **SQLAlchemy**: ORM 및 데이터베이스 관리
- **Alembic**: 데이터베이스 마이그레이션
- **JWT**: 사용자 인증
- **Pydantic**: 데이터 검증

### 프론트엔드

- **React 18**: 사용자 인터페이스
- **TypeScript**: 타입 안전성
- **Vite**: 빠른 개발 서버 및 빌드 도구
- **Tailwind CSS**: 스타일링
- **React Router**: 클라이언트 사이드 라우팅
- **Axios**: HTTP 클라이언트

## 프로젝트 구조

```
/
├── backend/          # FastAPI 백엔드
│   ├── app/
│   │   ├── models/   # 데이터베이스 모델
│   │   ├── schemas/  # Pydantic 스키마
│   │   ├── routes/   # API 라우트
│   │   └── main.py   # 메인 애플리케이션
│   └── requirements.txt
├── frontend/         # React 프론트엔드
│   ├── src/
│   │   ├── components/
│   │   ├── contexts/
│   │   ├── services/
│   │   └── types/
│   └── package.json
└── README.md
```

## 실행 방법

### 1. 백엔드 실행

#### uv 사용 (권장)

```bash
cd backend

# 의존성 설치
uv sync

# 서버 실행
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### pip 사용

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 프론트엔드 실행

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

### 3. 브라우저에서 접속

- 프론트엔드: http://localhost:3000
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs

## 환경 설정

### 백엔드 환경변수

`.env` 파일을 `backend/` 디렉토리에 생성:

```env
DATABASE_URL=sqlite:///./chat_app.db
SECRET_KEY=your-secret-key-here
```

### 프론트엔드 설정

`frontend/vite.config.ts`에서 API 프록시 설정 확인:

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, '')
  }
}
```

## 데이터 파이프라인 및 RAG 구성

- **데이터 전처리**: `data_etl/raw_data_split_mysql/steam_data_save_정형_비정형_나누기-github.ipynb`에서 Kaggle Steam 원본 CSV를 정형/비정형 컬럼으로 분리하고, 각각 CSV/JSON으로 저장합니다.
- **Text-to-SQL 적재**: `data_etl/raw_data_split_mysql/steam_data_save_JSON_mysql-github.ipynb`이 정형 JSON(`steam_games_structured_data.json`)을 읽어 MySQL 데이터베이스(`steam_structured_db`)를 생성하고 `steam_structured_data` 테이블에 로드합니다.
- **그래프 & 벡터 인덱싱**: `data_etl/LLM_RAG_DB_생성_RAG_테스트/ingest_data.py`가 비정형 JSON(`config.JSON_DATA_PATH`)을 Neo4j 그래프(게임-개발사/배급사/장르/카테고리 관계)와 Qdrant 벡터 DB에 동기화합니다. 임베딩 모델과 DB 엔드포인트는 `config.py`에서 환경 변수로 관리합니다.
- **질의 파이프라인**: `data_etl/LLM_RAG_DB_생성_RAG_테스트/rag_engine.py`는 질의를 Gemini로 분해(엔티티/시맨틱 쿼리), Qdrant에서 벡터 검색 후 Neo4j 필터링으로 컨텍스트를 확장하고, 재차 Gemini로 최종 답변을 생성하는 하이브리드 RAG 흐름을 제공합니다.

### 실행 순서 요약

1. Kaggle CSV → 전처리 노트북 실행으로 정형/비정형 데이터 분리.
2. 정형 JSON → Text-to-SQL 노트북 실행으로 MySQL에 적재.
3. 비정형 JSON → ingest_data.py 실행으로 Neo4j 및 Qdrant 인덱싱.
4. RAGEngine을 사용해 질의를 전달하면, 위 인덱스를 활용한 RAG 답변이 생성됩니다.

- 각 단계는 독립 실행 가능하지만, 순차적으로 수행하는 것이 좋습니다.

## 데이터베이스 모델

### User 모델

- 사용자 기본 정보 (username, email, password)
- 계정 상태 및 권한 관리

### Chat 모델

- 채팅 세션 관리
- 사용자별 채팅 목록

### Message 모델

- 채팅 메시지 저장
- 사용자/AI 역할 구분

## API 엔드포인트

### 인증

- POST /auth/register: 회원가입
- POST /auth/login: 로그인
- GET /auth/me: 현재 사용자 정보

### 채팅

- GET /chat/: 사용자 채팅 목록
- POST /chat/: 새 채팅 생성
- GET /chat/{chat_id}: 특정 채팅 조회
- PUT /chat/{chat_id}: 채팅 수정
- DELETE /chat/{chat_id}: 채팅 삭제

### 메시지

- POST /chat/{chat_id}/messages: 메시지 전송
- GET /chat/{chat_id}/messages: 채팅 메시지 목록

