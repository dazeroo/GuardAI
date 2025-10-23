# 웹 취약점 자동 진단 스크립트

권한이 있는 시스템에 대해서만 사용하세요. 무단 스캔은 법적 문제를 일으킬 수 있습니다.

## 📁 프로젝트 구조

```
web_vulnerability_scanner/
│
├── main.py                          # 메인 실행 파일
├── config.py                        # 설정 파일
├── requirements.txt                 # 필요 라이브러리
├── README.md                        # 이 파일
│
├── modules/                         # 취약점 검사 모듈
│   ├── __init__.py
│   ├── sql_injection.py            # 1. SQL 인젝션
│   ├── xss.py                      # 2. XSS
│   ├── directory_indexing.py       # 3. 디렉터리 인덱싱
│   ├── security_headers.py         # 4. 보안 헤더
│   ├── cookie_security.py          # 5. 쿠키 보안 속성
│   ├── csrf_protection.py          # 6. CSRF 토큰
│   ├── ssi_injection.py            # 7. SSI 인젝션
│   ├── ldap_injection.py           # 8. LDAP 인젝션
│   ├── xpath_injection.py          # 9. XPath 인젝션
│   ├── file_upload.py              # 10. 파일 업로드
│   ├── file_download.py            # 11. 파일 다운로드
│   └── weak_crypto.py              # 12. 약한 암호화
│
├── utils/                           # 유틸리티
│   ├── __init__.py
│   ├── http_client.py              # HTTP 요청 처리
│   └── report_generator.py         # 리포트 생성
│
└── reports/                         # 결과 리포트 (자동 생성)
```

## 🚀 설치 방법

### 1. Python 설치 확인
```bash
python --version  # Python 3.7 이상 필요
```

### 2. 프로젝트 디렉터리 생성
```bash
mkdir web_vulnerability_scanner
cd web_vulnerability_scanner
```

### 3. 디렉터리 구조 생성
```bash
# Windows
mkdir modules utils reports

# Linux/Mac
mkdir -p modules utils reports
```

### 4. 파일 복사
각 파일을 해당 위치에 저장:
- `main.py` → 루트 디렉터리
- `config.py` → 루트 디렉터리
- `requirements.txt` → 루트 디렉터리
- `modules/*.py` → modules 디렉터리
- `utils/*.py` → utils 디렉터리

### 5. 필요 라이브러리 설치
```bash
pip install -r requirements.txt
```

## 💻 사용 방법

### 기본 사용
```bash
python main.py
```

# 웹 취약점 자동 진단 스크립트

권한이 있는 시스템에 대해서만 사용하세요. 무단 스캔은 법적 문제를 일으킬 수 있습니다.

## 📁 프로젝트 구조

```
web_vulnerability_scanner/
│
├── main.py                          # 메인 실행 파일
├── config.py                        # 설정 파일
├── requirements.txt                 # 필요 라이브러리
├── README.md                        # 이 파일
│
├── modules/                         # 취약점 검사 모듈
│   ├── __init__.py
│   ├── sql_injection.py            # 1. SQL 인젝션
│   ├── xss.py                      # 2. XSS
│   ├── directory_indexing.py       # 3. 디렉터리 인덱싱
│   ├── security_headers.py         # 4. 보안 헤더
│   ├── cookie_security.py          # 5. 쿠키 보안 속성
│   ├── csrf_protection.py          # 6. CSRF 토큰
│   ├── ssi_injection.py            # 7. SSI 인젝션
│   ├── ldap_injection.py           # 8. LDAP 인젝션
│   ├── xpath_injection.py          # 9. XPath 인젝션
│   ├── file_upload.py              # 10. 파일 업로드
│   ├── file_download.py            # 11. 파일 다운로드
│   └── weak_crypto.py              # 12. 약한 암호화
│
├── utils/                           # 유틸리티
│   ├── __init__.py
│   ├── http_client.py              # HTTP 요청 처리
│   └── report_generator.py         # 리포트 생성
│
└── reports/                         # 결과 리포트 (자동 생성)
```

## 🚀 설치 방법

### 1. Python 설치 확인
```bash
python --version  # Python 3.7 이상 필요
```

### 2. 프로젝트 디렉터리 생성
```bash
mkdir web_vulnerability_scanner
cd web_vulnerability_scanner
```

### 3. 디렉터리 구조 생성
```bash
# Windows
mkdir modules utils reports

# Linux/Mac
mkdir -p modules utils reports
```

### 4. 파일 복사
각 파일을 해당 위치에 저장:
- `main.py` → 루트 디렉터리
- `config.py` → 루트 디렉터리
- `requirements.txt` → 루트 디렉터리
- `modules/*.py` → modules 디렉터리
- `utils/*.py` → utils 디렉터리

### 5. 필요 라이브러리 설치
```bash
pip install -r requirements.txt
```

## 💻 사용 방법

### 기본 사용
```bash
python main.py
```

실행 후:
1. 진단할 URL 입력
2. 검사 항목 선택
   - **전체 검사**: 그냥 Enter
   - **선택 검사**: 번호 입력 (예: `1,2,5` 또는 `1-5` 또는 `13-20`)

### 사용 예시

```bash
$ python main.py

======================================================================
              웹 취약점 자동 진단 스크립트 v2.0
======================================================================

진단할 URL을 입력하세요: https://example.com

======================================================================
검사 항목 선택
======================================================================

[항목]
  1. SQL 인젝션
  2. XSS (크로스사이트 스크립팅)
  ...
  13. 데이터 평문 전송
  14. 정보 누출
  ...

======================================================================
전체 검사: Enter
선택 검사: 번호 입력 (예: 1,2,5 또는 1-5)
======================================================================

선택: 1-5,13,14

선택된 항목: [1, 2, 3, 4, 5, 13, 14]

[*] 1. SQL 인젝션 검사 중...
    🟢 양호: SQL 인젝션 취약점이 발견되지 않았습니다
...
```

## 📊 검사 항목 (총 20개)

### 항목
| 번호 | 취약점 항목 | 설명 |
|------|-------------|------|
| 1 | SQL 인젝션 | 데이터베이스 쿼리 조작 취약점 |
| 2 | XSS | 악성 스크립트 삽입 취약점 |
| 3 | 디렉터리 인덱싱 | 파일 목록 노출 |
| 4 | 보안 헤더 | 필수 보안 헤더 설정 확인 |
| 5 | 쿠키 보안 속성 | Secure, HttpOnly, SameSite 확인 |
| 6 | CSRF 토큰 | CSRF 보호 메커니즘 확인 |
| 7 | SSI 인젝션 | Server Side Includes 실행 |
| 8 | LDAP 인젝션 | LDAP 쿼리 조작 |
| 9 | XPath 인젝션 | XPath 쿼리 조작 |
| 10 | 파일 업로드 | 위험한 파일 업로드 가능성 |
| 11 | 파일 다운로드 | 경로 조작(Path Traversal) |
| 12 | 약한 암호화 | MD5, SHA-1, DES 등 사용 확인 |
| 13 | 데이터 평문 전송 | HTTP 사용, HSTS 미설정 확인 |
| 14 | 정보 누출 | 에러 메시지, 주석, 설정 파일 노출 |
| 15 | 위치 공개 | 민감한 경로/파일 노출 |
| 16 | 세션 고정 | 세션 ID 고정 공격 취약점 |
| 17 | 쿠키 변조 | 쿠키 암호화/서명 확인 |
| 18 | 운영체제 명령 실행 | Command Injection 취약점 |
| 19 | 불충분한 인증 | 인증 우회, 기본 자격증명 |
| 20 | 세션 예측 | 세션 ID 예측 가능성 |

## 📈 결과 해석

### 🔴 취약
- 명확한 취약점이 발견됨
- 즉시 조치 필요

### 🟢 양호
- 취약점이 발견되지 않음
- 현재 상태 유지

### 🟡 인터뷰
- 추가 수동 확인 필요
- 자동화로 판단 불가능한 경우

## 📄 리포트

스캔 완료 후 `reports/` 디렉터리에 자동 저장:
- `scan_report_YYYYMMDD_HHMMSS.json` - JSON 형식 리포트
- `scan_report_YYYYMMDD_HHMMSS.html` - HTML 형식 리포트 (브라우저에서 열기)

### JSON 리포트 구조
```json
{
  "target_url": "https://example.com",
  "scan_time": "2025-10-17 14:30:00",
  "summary": {
    "취약": 2,
    "양호": 15,
    "인터뷰": 3
  },
  "results": {
    "1. SQL 인젝션": {
      "status": "취약",
      "description": "...",
      "details": [...]
    }
  }
}
```

### HTML 리포트
- 웹 브라우저에서 보기 좋은 형식
- 색상 코딩된 결과
- 상세 정보 포함-10-17 14:30:00",
  "summary": {
    "취약": 2,
    "양호": 8,
    "인터뷰": 2
  },
  "results": {
    "1. SQL 인젝션": {
      "status": "취약",
      "description": "...",
      "details": [...]
    }
  }
}
```

## ⚙️ 설정 커스터마이징

`config.py` 파일에서 설정 변경 가능:

```python
REQUEST_TIMEOUT = 10        # 요청 타임아웃 (초)
MAX_RETRIES = 3            # 최대 재시도 횟수
VERIFY_SSL = False         # SSL 인증서 검증
```

## 🔧 개별 모듈 사용

특정 취약점만 검사하고 싶다면:

```python
from modules.sql_injection import test_sql_injection
from utils.http_client import create_session

session = create_session()
result = test_sql_injection("https://example.com?id=1", session)
print(result)
```

## ⚠️ 주의사항

1. **법적 책임**: 권한이 없는 시스템에 대한 스캔은 불법입니다
2. **네트워크 부하**: 과도한 요청으로 서버에 부하를 줄 수 있습니다
3. **False Positive**: 자동화 도구는 오탐이 발생할 수 있으니 수동 확인 필요
4. **제한사항**: 
   - 인증이 필요한 페이지는 검사 불가
   - JavaScript로 동적 생성되는 콘텐츠는 일부 탐지 불가
   - 복잡한 로직의 취약점은 수동 검사 필요

## 🐛 문제 해결

### SSL 인증서 오류
```bash
# config.py에서 VERIFY_SSL = False로 설정됨
# 필요시 True로 변경
```

### 모듈 import 오류
```bash
# __init__.py 파일이 각 디렉터리에 있는지 확인
# Python 경로 확인
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 타임아웃 오류
```bash
# config.py에서 REQUEST_TIMEOUT 값 증가
REQUEST_TIMEOUT = 30
```

## 📝 예제

### 1. 기본 스캔
```bash
$ python main.py
진단할 URL을 입력하세요: https://testsite.com

======================================================================
웹 취약점 진단 시작
======================================================================
대상 URL: https://testsite.com
시작 시간: 2025-10-17 14:30:00
======================================================================

[*] 1. SQL 인젝션 검사 중...
    🟢 양호: SQL 인젝션 취약점이 발견되지 않았습니다

[*] 2. XSS (크로스사이트 스크립팅) 검사 중...
    🔴 취약: XSS 취약점이 발견되었습니다
       - 파라미터 'search'에서 XSS 가능: 입력값이 필터링 없이 반영됨

...
```

### 2. 파라미터가 있는 URL
```bash
$ python main.py
진단할 URL을 입력하세요: https://testsite.com/search?q=test&page=1
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. Python 버전 (3.7 이상)
2. 필요 라이브러리 설치 여부
3. 네트워크 연결 상태
4. 대상 URL 접근 가능 여부

## 📚 참고 자료

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide/

## 🤝 기여

추가하고 싶은 취약점 검사 모듈이 있다면:
1. `modules/` 디렉터리에 새 파일 생성
2. `test_[취약점명]` 함수 구현
3. `main.py`와 `modules/__init__.py`에 추가

---

**면책 조항**: 이 도구는 교육 및 합법적인 보안 테스트 목적으로만 사용되어야 합니다. 작성자는 이 도구의 오용에 대해 책임지지 않습니다.