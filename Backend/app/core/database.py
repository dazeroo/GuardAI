import os
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import pymysql
pymysql.install_as_MySQLdb()

logger = logging.getLogger("uvicorn")

# 1. 환경변수에서 DATABASE_URL을 먼저 확인합니다.
# DATABASE_URL = os.environ.get(
#     "DATABASE_URL", 
#     f"sqlite:///{Path(__file__).resolve().parent.parent.parent / 'app_data.db'}"
# )
db_url_from_env = os.environ.get("DATABASE_URL")

if db_url_from_env:
    DATABASE_URL = db_url_from_env
    logger.info(f"환경변수에서 데이터베이스 정보를 불러왔습니다: {DATABASE_URL}")
else:
    default_db_path = f"sqlite:///{Path(__file__).resolve().parent.parent.parent / 'app_data.db'}"
    DATABASE_URL = default_db_path
    logger.info("환경변수에 설정된 데이터베이스 정보가 없습니다. 기본 SQLite로 연결합니다.")
    logger.info(f"SQLite DB 경로: {DATABASE_URL}")

# 2. 데이터베이스 엔진 생성
engine_args = {}
if DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_args)

# 3. 데이터베이스 세션 생성기
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# 4. SQLAlchemy 모델의 기본이 될 Base 클래스
Base = declarative_base()

# 5. API 라우터에서 사용할 데이터베이스 의존성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()