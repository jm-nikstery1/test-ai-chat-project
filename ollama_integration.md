# Ollama LLM 연동 가이드

## 📋 개요

채팅 시스템에 [Ollama Python 라이브러리](https://github.com/ollama/ollama-python)를 사용하여 실제 LLM과 연결했습니다. `gemma3:latest` 모델을 사용하여 실제 AI 응답을 생성합니다.

## 🔧 설치 및 설정

### 1. Ollama 서비스 설치

```bash
# Ollama 설치 (Linux)
curl -fsSL https://ollama.com/install.sh | sh

# 또는 공식 웹사이트에서 다운로드
# https://ollama.com/download
```

### 2. Ollama 서비스 실행

```bash
# Ollama 서비스 시작
ollama serve

# 백그라운드에서 실행하려면
nohup ollama serve > ollama.log 2>&1 &
```

### 3. gemma3 모델 다운로드

```bash
# gemma3:latest 모델 다운로드
ollama pull gemma3:latest

# 설치된 모델 확인
ollama list
```

### 4. Python 패키지 설치

```bash
cd /home/herss101/Desktop/home_sort/test-cursor/test-new-cursor-app-1/backend
uv pip install ollama==0.5.3
```

## 🚀 코드 변경사항

### 1. requirements.txt 업데이트

```txt
# 추가된 패키지
ollama==0.5.3
```

### 2. generate_ai_response 함수 수정

**변경 전 (임시 응답)**:

```python
def generate_ai_response(user_message: str) -> str:
    responses = [
        f"'{user_message}'에 대한 흥미로운 질문이네요!",
        # ... 기타 임시 응답들
    ]
    # 해시 기반 응답 선택
    return responses[response_index]
```

**변경 후 (Ollama 연동)**:

```python
def generate_ai_response(user_message: str) -> str:
    """
    Ollama를 사용한 AI 응답 생성 함수
    gemma3:latest 모델을 사용하여 실제 LLM 응답을 생성합니다.
    """
    try:
        import ollama

        # Ollama 클라이언트 생성
        client = ollama.Client()

        logger.info(f"Ollama에 메시지 전송: {user_message[:50]}...")

        # gemma3:latest 모델로 채팅 요청
        response = client.chat(
            model='gemma3:latest',
            messages=[
                {
                    'role': 'user',
                    'content': user_message,
                }
            ]
        )

        ai_response = response['message']['content']
        logger.info(f"Ollama 응답 수신: {ai_response[:50]}...")

        return ai_response

    except ImportError:
        logger.error("ollama 패키지가 설치되지 않았습니다.")
        return f"AI 서비스가 설정되지 않았습니다. 사용자님의 메시지: '{user_message}'"

    except Exception as e:
        logger.error(f"Ollama 연결 실패: {e}")
        return f"죄송합니다. 현재 AI 서비스에 연결할 수 없습니다. 사용자님의 메시지: '{user_message}'"
```

## 🔄 동작 흐름

### 메시지 전송 프로세스

1. **사용자가 메시지 입력** → 프론트엔드
2. **`/chat/{chat_id}/send-message` API 호출** → 백엔드
3. **사용자 메시지 저장** → 데이터베이스
4. **`generate_ai_response()` 호출** → 백엔드
5. **Ollama 클라이언트 생성** → `ollama.Client()`
6. **gemma3:latest 모델로 요청** → Ollama 서비스
7. **AI 응답 수신** → 백엔드
8. **AI 응답 저장** → 데이터베이스
9. **두 메시지 모두 반환** → 프론트엔드

## 🛠️ 설정 확인

### 1. Ollama 서비스 상태 확인

```bash
# Ollama 서비스 실행 상태 확인
ps aux | grep ollama

# 또는 포트 확인 (기본: 11434)
netstat -tlnp | grep 11434
```

### 2. 모델 설치 확인

```bash
# 설치된 모델 목록
ollama list

# gemma3 모델 테스트
ollama run gemma3:latest "안녕하세요"
```

### 3. Python에서 테스트

```python
import ollama

# 클라이언트 생성
client = ollama.Client()

# 채팅 테스트
response = client.chat(
    model='gemma3:latest',
    messages=[{'role': 'user', 'content': '안녕하세요'}]
)

print(response['message']['content'])
```

## 🔧 문제 해결

### 1. Ollama 서비스가 실행되지 않는 경우

```bash
# Ollama 서비스 시작
ollama serve

# 로그 확인
tail -f ollama.log
```

### 2. 모델이 설치되지 않은 경우

```bash
# gemma3 모델 다운로드
ollama pull gemma3:latest

# 다른 모델 사용 (예: llama2)
ollama pull llama2:latest
```

### 3. 연결 오류가 발생하는 경우

```python
# 코드에서 모델명 확인
response = client.chat(
    model='gemma3:latest',  # 정확한 모델명 사용
    messages=[...]
)
```

## 📊 성능 고려사항

### 1. 응답 시간

- **로컬 모델**: 1-5초 (하드웨어에 따라 다름)
- **네트워크 지연**: 최소화됨 (로컬 실행)

### 2. 메모리 사용량

- **gemma3:latest**: 약 2-4GB RAM 필요
- **서버 사양**: 최소 8GB RAM 권장

### 3. 모델 선택

```python
# 가벼운 모델 (빠른 응답)
model='gemma3:2b'

# 중간 모델 (균형)
model='gemma3:latest'

# 큰 모델 (고품질)
model='llama2:70b'
```

## 🔮 향후 개선사항

### 1. 스트리밍 응답

```python
# 스트리밍 응답 구현
stream = client.chat(
    model='gemma3:latest',
    messages=[{'role': 'user', 'content': user_message}],
    stream=True
)

for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)
```

### 2. 대화 컨텍스트 유지

```python
# 이전 메시지들을 포함한 대화 컨텍스트
messages = [
    {'role': 'system', 'content': '당신은 도움이 되는 AI 어시스턴트입니다.'},
    {'role': 'user', 'content': '이전 메시지 1'},
    {'role': 'assistant', 'content': '이전 응답 1'},
    {'role': 'user', 'content': user_message}
]
```

### 3. 모델 설정 최적화

```python
# 모델 파라미터 조정
response = client.chat(
    model='gemma3:latest',
    messages=[...],
    options={
        'temperature': 0.7,
        'top_p': 0.9,
        'max_tokens': 1000
    }
)
```

## 📝 로깅

### 로그 레벨 설정

```python
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ollama 요청/응답 로깅
logger.info(f"Ollama 요청: {user_message}")
logger.info(f"Ollama 응답: {ai_response}")
```

## 🎯 테스트 시나리오

1. **Ollama 서비스 실행** → `ollama serve`
2. **모델 다운로드** → `ollama pull gemma3:latest`
3. **백엔드 서버 실행** → `uv run uvicorn main:app --host 0.0.0.0 --port 8000`
4. **프론트엔드 실행** → `npm run dev`
5. **채팅 테스트** → 실제 AI 응답 확인

이제 채팅 시스템이 실제 LLM과 연결되어 진짜 AI 응답을 생성합니다! 🚀
