from fastapi import APIRouter, Depends, UploadFile
from pydantic import BaseModel, SecretStr, HttpUrl
from enum import Enum
from typing import Optional
from uuid import uuid4
import os
import aiofiles
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, create_engine, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.api.v1.io_models import FileIn, FileOut

# ---------- DB 연결 ----------
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///../../../app_data.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# ---------- 테이블 ----------
class WebTarget(Base):
    __tablename__ = "web_targets"
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    url = Column(Text, nullable=False)

class DBCredential(Base):
    __tablename__ = "db_credentials"
    id = Column(Integer, primary_key=True, index=True)
    cred_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    db_type = Column(String(20), nullable=False)
    host = Column(String(200), nullable=False)
    port = Column(Integer, nullable=False)
    database = Column(String(200), nullable=True)
    username = Column(String(200), nullable=False)
    password = Column(Text, nullable=False)  # ⚠️ 데모: 평문 저장. 운영환경에선 비밀관리 사용!

class File(Base):
    __tablename__ = 'files'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    file_name = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ---------- Pydantic 모델 ----------
class DBType(str, Enum):
    mysql = "mysql"
    postgres = "postgres"
    mssql = "mssql"

class SiteIn(BaseModel):
    url: HttpUrl

class SiteOut(BaseModel):
    site_id: str

class DBCredIn(BaseModel):
    db_type: DBType
    host: str
    port: int
    database: Optional[str] = None
    username: str
    password: SecretStr

class DBCredOut(BaseModel):
    cred_id: str

# ---------- 세션 의존성 ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- 라우터 ----------
router = APIRouter(prefix="/api/v1", tags=["store"])

# 사이트 입력 → 저장
@router.post("/web/targets", response_model=SiteOut)
def create_site(payload: SiteIn, db: Session = Depends(get_db)):
    site_id = str(uuid4())
    db.add(WebTarget(site_id=site_id, url=str(payload.url)))
    db.commit()
    return SiteOut(site_id=site_id)

# DB 계정 입력 → 저장
@router.post("/db/credentials", response_model=DBCredOut)
def create_db_cred(payload: DBCredIn, db: Session = Depends(get_db)):
    cred_id = str(uuid4())
    db.add(DBCredential(
        cred_id=cred_id,
        db_type=payload.db_type.value,
        host=payload.host,
        port=payload.port,
        database=payload.database or "",
        username=payload.username,
        # ⚠️ 데모: 평문 저장. 운영환경에선 암호화/비밀관리(KMS/Vault) 사용!
        password=payload.password.get_secret_value(),
    ))
    db.commit()
    return DBCredOut(cred_id=cred_id)

# 파일 저장 경로 설정
UPLOAD_DIRECTORY = "./reports"

@router.post("/files/upload", response_model=FileOut, tags=["files"])
async def upload_file(
    file: UploadFile,
    db: Session = Depends(get_db)
):
    # 파일 저장 디렉터리가 없으면 생성
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    # 파일명을 UUID 기반으로 생성하여 중복 방지
    file_id = str(uuid4())
    file_path = os.path.join(UPLOAD_DIRECTORY, f"{file_id}_{file.filename}")

    # 파일을 로컬 파일 시스템에 저장
    file_size = 0
    async with aiofiles.open(file_path, 'wb') as f:
        while contents := await file.read():
            file_size += len(contents)
            await f.write(contents)

    # DB에 파일 메타데이터 저장
    db_file = File(
        id=file_id,
        file_name=file.filename,
        content_type=file.content_type,
        file_size=file_size
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return db_file
