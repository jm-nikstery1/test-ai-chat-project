# Backend Import Error 해결 방법

## 🚨 발생한 오류

```
ImportError: cannot import name 'Base' from 'app.models' (/home/herss101/Desktop/home_sort/test-cursor/test-new-cursor-app-1/backend/app/models/__init__.py)
```

## 🔍 문제 분석

### 원인

- `main.py`에서 `from app.models import Base`를 시도했지만
- `app/models/__init__.py`에서 `Base`를 export하지 않았음
- `Base`는 `app/database.py`에 정의되어 있음

### 오류 발생 위치

```python
# backend/app/main.py
from app.models import Base  # ❌ Base를 찾을 수 없음
```

## ✅ 해결 방법

### 1. models/**init**.py 수정

**수정 전:**

```python
from .user import User
from .chat import Chat, Message

__all__ = ["User", "Chat", "Message"]
```

**수정 후:**

```python
from .user import User
from .chat import Chat, Message
from app.database import Base  # ✅ Base import 추가

__all__ = ["User", "Chat", "Message", "Base"]  # ✅ __all__에 Base 추가
```

### 2. uv 패키지 관리 지원 추가

#### pyproject.toml 생성

```toml
[project]
name = "llm-chat-backend"
version = "1.0.0"
description = "LLM Chat Backend with FastAPI"
requires-python = ">=3.10"
dependencies = [
    "fastapi==0.104.1",
    "uvicorn[standard]==0.24.0",
    "sqlalchemy==2.0.23",
    "alembic==1.12.1",
    "psycopg2-binary==2.9.9",
    "python-multipart==0.0.6",
    "python-jose[cryptography]==3.3.0",
    "passlib[bcrypt]==1.7.4",
    "python-dotenv==1.0.0",
    "pydantic==2.5.0",
    "pydantic-settings==2.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.24.0",
]
```

#### 실행 스크립트 업데이트 (run_backend.sh)

```bash
#!/bin/bash

echo "🚀 LLM Chat Backend 시작 중..."

# 백엔드 디렉토리로 이동
cd backend

# uv를 사용한 의존성 설치 및 서버 실행
echo "📚 의존성 설치 중..."
uv sync

# 서버 실행
echo "🌐 서버 시작 중... (http://localhost:8000)"
echo "📖 API 문서: http://localhost:8000/docs"
echo "🔍 API 탐색: http://localhost:8000/redoc"
echo ""
echo "서버를 중지하려면 Ctrl+C를 누르세요."
echo ""

uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🎯 핵심 해결 포인트

### 1. Import 경로 문제

- **문제**: `Base`가 `database.py`에 있지만 `models/__init__.py`에서 export되지 않음
- **해결**: `models/__init__.py`에서 `Base`를 import하고 `__all__`에 추가

### 2. 모듈 구조 이해

```
app/
├── database.py      # Base 정의
├── models/
│   ├── __init__.py  # Base를 export해야 함
│   ├── user.py
│   └── chat.py
└── main.py          # Base를 import
```

### 3. uv 패키지 관리자 지원

- **기존**: pip + requirements.txt
- **개선**: uv + pyproject.toml
- **장점**: 더 빠른 의존성 설치, 자동 가상환경 관리

## 🚀 실행 방법

### uv 사용 (권장)

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### pip 사용

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📝 교훈

1. **모듈 구조 설계**: `__init__.py`에서 필요한 모든 클래스/함수를 export해야 함
2. **Import 경로 관리**: 상대 import와 절대 import를 적절히 사용
3. **패키지 관리**: 현대적인 도구(uv) 사용으로 개발 효율성 향상
4. **에러 메시지 분석**: ImportError는 보통 모듈 구조나 경로 문제

## 🔧 추가 개선사항

- `pyproject.toml`로 의존성 관리 표준화
- uv를 통한 빠른 패키지 설치
- 개발 의존성 분리 (pytest, httpx 등)
- 빌드 시스템 설정 (hatchling)
