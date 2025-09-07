# 로그인 422 Unprocessable Entity 에러 해결

## 문제 상황

- 회원가입: 정상 작동 (200 OK)
- 로그인: 422 Unprocessable Entity 에러 발생

## 원인 분석

### 1. 데이터 전송 형식 불일치

- **백엔드**: `OAuth2PasswordRequestForm` 사용 → `application/x-www-form-urlencoded` 형태 기대
- **프론트엔드**: JSON 형태로 `{ username, password }` 전송 → `application/json` 형태

### 2. 스키마 불일치

- **백엔드 로그인 엔드포인트**:
  ```python
  def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
  ```
- **프론트엔드 API 호출**:
  ```typescript
  login: (data: LoginCredentials) =>
    api.post<AuthResponse>('/auth/login', data),
  ```

## 해결 방법

### 1. 백엔드 수정

`/backend/app/routes/auth.py` 파일에서 로그인 엔드포인트를 수정:

**변경 전:**

```python
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    # ...
```

**변경 후:**

```python
@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    # ...
```

### 2. 스키마 import 추가

```python
from app.schemas.user import UserCreate, User as UserSchema, Token, UserLogin
```

## 수정된 코드

### 백엔드 (`/backend/app/routes/auth.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema, Token, UserLogin
from app.auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    # 사용자 확인
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # 액세스 토큰 생성
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
```

## 결과

- 프론트엔드에서 JSON 형태로 전송하는 로그인 데이터를 백엔드에서 정상적으로 받을 수 있게 됨
- 422 Unprocessable Entity 에러 해결
- 로그인 기능 정상 작동

## 참고사항

- `OAuth2PasswordRequestForm`은 OAuth2 표준에 따라 form-data 형태를 기대함
- REST API에서는 일반적으로 JSON 형태의 데이터를 사용하는 것이 더 일반적
- 프론트엔드와 백엔드 간의 데이터 전송 형식을 일치시키는 것이 중요
