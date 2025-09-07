# 인증 함수 구조 정리 및 리팩토링

## 📋 정리된 구조

### **`app/auth.py` - 인증 핵심 로직**

#### `get_current_user()`

```python
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    JWT 토큰을 검증하여 현재 로그인한 사용자 정보를 반환합니다.
    토큰이 유효하지 않거나 사용자가 존재하지 않으면 401 에러를 발생시킵니다.
    """
```

**역할:**

- JWT 토큰 검증
- 사용자 정보 조회
- 기본적인 인증 처리

#### `get_current_active_user()`

```python
def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    현재 로그인한 사용자 중 활성 상태인 사용자만 반환합니다.
    비활성 사용자에 대해서는 400 에러를 발생시킵니다.
    """
```

**역할:**

- 활성 사용자만 허용
- 보안이 강화된 인증
- 비활성 사용자 차단

### **`app/routes/auth.py` - 인증 엔드포인트**

#### `get_my_info()`

```python
@router.get("/me", response_model=UserSchema)
def get_my_info(current_user: User = Depends(get_current_user)):
    """현재 로그인한 사용자의 정보를 반환합니다."""
    return current_user
```

**역할:**

- `/auth/me` 엔드포인트 제공
- 현재 로그인한 사용자 정보 반환
- 프론트엔드에서 사용자 정보 조회 시 사용

### **`app/routes/chat.py` - 채팅 엔드포인트**

```python
def create_chat(..., current_user: User = Depends(get_current_active_user)):
def get_user_chats(..., current_user: User = Depends(get_current_active_user)):
```

**역할:**

- 보안이 중요한 채팅 기능에서 활성 사용자만 허용
- 비활성 사용자는 채팅 기능 사용 불가

## 🔄 변경 사항

### 1. 함수명 개선

- **변경 전**: `get_current_user_info()`
- **변경 후**: `get_my_info()`
- **이유**: 엔드포인트 함수명을 더 직관적으로 변경

### 2. 주석 추가

- 각 함수의 역할과 동작 방식에 대한 명확한 설명 추가
- 한국어 주석으로 이해하기 쉽게 작성

### 3. 역할 분리 명확화

- **`auth.py`**: 인증 로직 (JWT 검증, 사용자 조회)
- **`routes/auth.py`**: 인증 관련 API 엔드포인트
- **`routes/chat.py`**: 채팅 관련 API 엔드포인트

## 🛡️ 보안 레벨 구분

### Level 1: 기본 인증 (`get_current_user`)

- **사용처**: 사용자 정보 조회, 일반적인 API 접근
- **검증**: JWT 토큰 유효성만 확인
- **에러**: 401 Unauthorized (토큰 무효)

### Level 2: 강화된 인증 (`get_current_active_user`)

- **사용처**: 채팅 생성, 메시지 전송, 중요한 작업
- **검증**: JWT 토큰 + 사용자 활성 상태 확인
- **에러**: 401 Unauthorized (토큰 무효) + 400 Bad Request (비활성 사용자)

## 📊 사용 패턴

| 기능             | 사용 함수                 | 보안 레벨 | 설명               |
| ---------------- | ------------------------- | --------- | ------------------ |
| 사용자 정보 조회 | `get_current_user`        | Level 1   | 기본 인증만 필요   |
| 채팅 생성        | `get_current_active_user` | Level 2   | 활성 사용자만 허용 |
| 메시지 전송      | `get_current_active_user` | Level 2   | 활성 사용자만 허용 |
| 채팅 목록 조회   | `get_current_active_user` | Level 2   | 활성 사용자만 허용 |

## 🚀 장점

1. **명확한 책임 분리**: 각 함수의 역할이 명확하게 구분됨
2. **보안 레벨 구분**: 기능별로 적절한 보안 수준 적용
3. **유지보수성 향상**: 코드 구조가 명확하여 수정이 용이
4. **가독성 개선**: 함수명과 주석으로 이해하기 쉬움
5. **확장성**: 새로운 인증 레벨 추가가 용이

## 🔧 Import 구조

```python
# auth.py에서 export
def get_current_user(...) -> User
def get_current_active_user(...) -> User

# routes/auth.py에서 import
from app.auth import get_current_user

# routes/chat.py에서 import
from app.auth import get_current_active_user
```

## 📝 참고사항

- `get_current_user`는 `get_current_active_user`의 기반이 됨
- 모든 인증 함수는 FastAPI의 `Depends`를 사용하여 의존성 주입
- JWT 토큰은 `Authorization: Bearer <token>` 형태로 전송
- 토큰 만료 시 자동으로 401 에러 반환
