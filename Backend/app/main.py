import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.models import init_db
from app.routers.v2 import items, targets, tech_summary, upload

# .env 파일에서 환경변수를 불러옵니다.
load_dotenv()

# 이제 os.environ을 통해 환경변수를 사용할 수 있습니다.
db_url = os.getenv("DATABASE_URL")
secret = os.getenv("SECRET_KEY")

app = FastAPI(title="GuardAI API")

# 서버 시작 시 데이터베이스를 초기화하는 이벤트 핸들러
@app.on_event("startup")
def on_startup():
    """
    FastAPI 애플리케이션이 시작될 때 단 한 번 실행되는 함수입니다.
    이곳에서 init_db()를 호출하여 데이터베이스 테이블을 생성합니다.
    """
    print("애플리케이션 시작... 데이터베이스 초기화를 진행합니다.")
    init_db()
    print("데이터베이스 초기화 완료.")
    
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],  # 개발 단계: 모두 허용, 운영에서는 도메인 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(items.router, prefix="/routers/v2")
app.include_router(targets.router, prefix="/routers/v2")
app.include_router(tech_summary.router, prefix="/routers/v2")
app.include_router(upload.router, prefix="/routers/v2")