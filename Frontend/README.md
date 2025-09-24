## 📝 개요 (Overview)

프론트엔드 초기 버전 개발을 완료하고 `main` 브랜치에 병합하기 위한 PR입니다.

---

## 🧪 테스트 방법 (How to Test)

1. `git checkout develop`
2. `npm install`
3. `npm run dev` (local에서만 접근 가능) or `npm run dev -- --host` (같은 네트워크 대역이면 접근 가능)
4. log에 나온 주소로 접속하여 UI 및 기능 확인

---

## ❗ 참고 사항 (Notes)

- 기술 컨설팅 섹션의 백엔드 기능 연동 예정
- 관리 컨설팅 섹션의 프론트 수정 예정

  ---  
  ### Figma React Fix (Vite + Tailwind)

  ### 빠른 실행
  ```bash
  npm i
  npm run dev
  ```

  ### 빌드
  ```bash
  npm run build
  npm run preview
  ```

  - 경로 별칭: `@` -> `src`
  - Tailwind 활성화됨 (`src/styles/globals.css`)
  - 소스는 `/src`에 배치됨 (원본 zip의 `App.tsx`, `components/**`, `styles/**` 등)
