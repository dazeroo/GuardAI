import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import pymysql
pymysql.install_as_MySQLdb()

# 1. 데이터베이스 연결 URL 설정
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    f"sqlite:///{Path(__file__).resolve().parent.parent.parent / 'app_data.db'}"
)

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