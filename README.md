# GuardAI

> GuardAI 통합 보안 컨설팅 서비스는 기술적 컨설팅 서비스와 관리적 컨설팅 서비스를 제공하며,
> 각 섹션별로 보고서 요약과 자동 진단 기능이 존재합니다.
---

## ✅ 전역 환경 설정 
```
sudo apt update
sudo apt install -y nodejs npm python3 python3-pip python3-venv git build-essential curl
# sudo apt install -y nodejs npm python3.11 python3.11-venv python3.11-distutils python3-pip git build-essential
```

### 해당 프로젝트에만 python3.11 설치 (pyenv)
- 전역 환경에 python3.11을 설치한 경우, 아래 pyenv 설정은 하지 않아도 됨.
    ```
    sudo apt update
    sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git

    # pyenv 설치 스크립트 실행
    curl https://pyenv.run | bash

    # 쉘 설정 파일에 pyenv 초기화 스크립트 없으면 추가 (.bashrc)
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
    echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc
    exec "$SHELL"

    pyenv install 3.11.9
    ```


## ✅ Backend Server
0. 저장소 클론
```
git clone https://github.com/dazeroo/GuardAI.git
```

1. 의존성 설치
```
cd Backend
pyenv local 3.11.9

# Python 가상환경 사용 권장
python -m venv venv   # python3.11 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

2. 환경변수 설정
- `.env.example` 파일을 참고하여 `.env` 파일 생성 및 수정

3. 서버 실행
```
uvicorn app.main:app --reload  # --host 0.0.0.0
```


## ✅ Frontend Server
1. 의존성 설치
```
cd Frontend
npm install
```
2. 개발 서버 실행
```
npm run dev -- --host
```
3. 빌드 (배포 시)
```
npm run build
```
