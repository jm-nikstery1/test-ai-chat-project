# Frontend Error 해결 방법

## 🚨 발생한 오류들

### 1. Tailwind CSS 모듈 누락 오류

```
Error: Loading PostCSS Plugin failed: Cannot find module 'tailwindcss'
Require stack:
- /home/herss101/Desktop/home_sort/test-cursor/test-new-cursor-app-1/frontend/postcss.config.js
```

### 2. ES Module 경고

```
Warning: Module type of file:///home/herss101/Desktop/home_sort/test-cursor/test-new-cursor-app-1/frontend/postcss.config.js is not specified and it doesn't parse as CommonJS.
Reparsing as ES module because module syntax was detected. This incurs a performance overhead.
To eliminate this warning, add "type": "module" to /home/herss101/Desktop/home_sort/test-cursor/test-new-cursor-app-1/frontend/package.json.
```

### 3. Vite CJS API 경고

```
The CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.
```

## 🔍 문제 분석

### 원인

1. **Tailwind CSS 누락**: `package.json`에 `tailwindcss`, `autoprefixer`, `postcss` 의존성이 없음
2. **ES Module 설정 누락**: `package.json`에 `"type": "module"` 설정이 없음
3. **PostCSS 설정 오류**: PostCSS가 Tailwind CSS를 찾을 수 없음

### 오류 발생 위치

- `postcss.config.js`: Tailwind CSS 플러그인을 로드할 수 없음
- `package.json`: ES Module 타입이 명시되지 않음

## ✅ 해결 방법

### 1. 기존 패키지 완전 삭제

```bash
cd frontend
rm -rf node_modules package-lock.json yarn.lock
```

### 2. package.json 수정

#### 2-1. ES Module 타입 추가

**수정 전:**

```json
{
  "name": "llm-chat-frontend",
  "version": "1.0.0",
  "description": "LLM Chat Frontend with TypeScript and React",
  "main": "index.js",
```

**수정 후:**

```json
{
  "name": "llm-chat-frontend",
  "version": "1.0.0",
  "description": "LLM Chat Frontend with TypeScript and React",
  "type": "module",
  "main": "index.js",
```

#### 2-2. Tailwind CSS 의존성 추가

**수정 전:**

```json
"devDependencies": {
  "@types/react": "^18.2.37",
  "@types/react-dom": "^18.2.15",
  "@typescript-eslint/eslint-plugin": "^6.10.0",
  "@typescript-eslint/parser": "^6.10.0",
  "@vitejs/plugin-react": "^4.1.1",
  "eslint": "^8.53.0",
  "eslint-plugin-react-hooks": "^4.6.0",
  "eslint-plugin-react-refresh": "^0.4.4",
  "typescript": "^5.2.2",
  "vite": "^5.0.0"
}
```

**수정 후:**

```json
"devDependencies": {
  "@types/react": "^18.2.37",
  "@types/react-dom": "^18.2.15",
  "@typescript-eslint/eslint-plugin": "^6.10.0",
  "@typescript-eslint/parser": "^6.10.0",
  "@vitejs/plugin-react": "^4.1.1",
  "eslint": "^8.53.0",
  "eslint-plugin-react-hooks": "^4.6.0",
  "eslint-plugin-react-refresh": "^0.4.4",
  "typescript": "^5.2.2",
  "vite": "^5.0.0",
  "tailwindcss": "^3.4.0",
  "autoprefixer": "^10.4.16",
  "postcss": "^8.4.32"
}
```

### 3. 패키지 재설치

```bash
npm install
```

### 4. Tailwind CSS 초기화

```bash
npx tailwindcss init -p
```

### 5. 프론트엔드 실행

```bash
npm run dev
```

## 🎯 핵심 해결 포인트

### 1. 의존성 관리

- **문제**: Tailwind CSS 관련 패키지가 설치되지 않음
- **해결**: `package.json`에 필요한 모든 의존성 추가

### 2. ES Module 설정

- **문제**: Node.js가 모듈 타입을 인식하지 못함
- **해결**: `package.json`에 `"type": "module"` 추가

### 3. PostCSS 설정

- **문제**: PostCSS가 Tailwind CSS 플러그인을 찾을 수 없음
- **해결**: Tailwind CSS 패키지 설치 및 초기화

## 🚀 실행 방법

### 완전한 재설치 및 실행

```bash
# 1. 기존 파일 삭제
cd frontend
rm -rf node_modules package-lock.json yarn.lock

# 2. 패키지 설치
npm install

# 3. Tailwind CSS 초기화
npx tailwindcss init -p

# 4. 개발 서버 실행
npm run dev
```

### 스크립트 사용

```bash
./run_frontend.sh
```

## 📝 해결된 문제들

1. ✅ **Tailwind CSS 모듈 누락**: `tailwindcss`, `autoprefixer`, `postcss` 패키지 추가
2. ✅ **ES Module 경고**: `"type": "module"` 설정 추가
3. ✅ **PostCSS 설정 오류**: Tailwind CSS 초기화로 해결
4. ✅ **Vite CJS API 경고**: ES Module 설정으로 해결

## 🔧 추가 개선사항

### package.json 최적화

- ES Module 타입 명시
- Tailwind CSS 관련 의존성 추가
- 개발 의존성과 프로덕션 의존성 분리

### PostCSS 설정

- `postcss.config.js` 자동 생성
- `tailwind.config.js` 자동 생성
- Vite와의 호환성 확보

## 🚨 주의사항

1. **Node.js 버전**: Vite 5.x는 Node.js 18+ 권장
2. **패키지 관리자**: npm, yarn, pnpm 모두 지원
3. **캐시 정리**: 문제 발생 시 `node_modules` 완전 삭제 후 재설치

## 📚 참고 자료

- [Vite ES Module 가이드](https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated)
- [Tailwind CSS 설치 가이드](https://tailwindcss.com/docs/installation)
- [PostCSS 설정 가이드](https://postcss.org/docs/postcss-config)

## 🎉 결과

프론트엔드가 정상적으로 실행되어 http://localhost:3000에서 접근 가능합니다!
