# LLM Chat Application

Open WebUI나 LibreChat과 같은 LLM 채팅 사이트를 FastAPI 백엔드와 TypeScript 프론트엔드로 구현한 프로젝트입니다.

## 🚀 주요 기능

- **사용자 인증**: JWT 기반 로그인/회원가입
- **채팅 관리**: 채팅 생성, 삭제, 메시지 저장
- **실시간 채팅**: 메시지 전송 및 응답
- **반응형 UI**: 모던하고 직관적인 사용자 인터페이스
- **데이터베이스**: SQLite/PostgreSQL 지원

## 🏗️ 기술 스택

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

## 📁 프로젝트 구조

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

## 🚀 실행 방법

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

## 🔧 환경 설정

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

## 📊 데이터베이스 모델

### User 모델

- 사용자 기본 정보 (username, email, password)
- 계정 상태 및 권한 관리

### Chat 모델

- 채팅 세션 관리
- 사용자별 채팅 목록

### Message 모델

- 채팅 메시지 저장
- 사용자/AI 역할 구분

## 🔐 API 엔드포인트

### 인증

- `POST /auth/register`: 회원가입
- `POST /auth/login`: 로그인
- `GET /auth/me`: 현재 사용자 정보

### 채팅

- `GET /chat/`: 사용자 채팅 목록
- `POST /chat/`: 새 채팅 생성
- `GET /chat/{chat_id}`: 특정 채팅 조회
- `PUT /chat/{chat_id}`: 채팅 수정
- `DELETE /chat/{chat_id}`: 채팅 삭제

### 메시지

- `POST /chat/{chat_id}/messages`: 메시지 전송
- `GET /chat/{chat_id}/messages`: 채팅 메시지 목록

## 🎨 UI 특징

- **반응형 디자인**: 모바일과 데스크톱 모두 지원
- **다크/라이트 모드**: 사용자 선호도에 따른 테마 변경
- **실시간 업데이트**: 메시지 전송 시 즉시 반영
- **직관적인 네비게이션**: 사이드바 기반 채팅 관리

## 🔮 향후 개발 계획

- [ ] 실제 LLM API 연동 (OpenAI, Anthropic 등)
- [ ] 파일 업로드 및 이미지 처리
- [ ] 채팅 내보내기/가져오기
- [ ] 다국어 지원
- [ ] 실시간 채팅 (WebSocket)
- [ ] 사용자 프로필 관리
- [ ] 채팅 검색 기능

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 생성해 주세요.
