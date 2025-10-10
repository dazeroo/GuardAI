from uuid import uuid4
import pytz   # KST
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime
)
from sqlalchemy.dialects.mysql import LONGBLOB 
from app.core.database import Base, engine

# SQLAlchemy 모델(테이블) 정의
class WebTarget(Base):
    __tablename__ = "web_targets"
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(String(36), unique=True, index=True, nullable=False)
    url = Column(Text, nullable=False)

class DBCredential(Base):
    __tablename__ = "db_credentials"
    id = Column(Integer, primary_key=True, index=True)
    cred_id = Column(String(36), unique=True, index=True, nullable=False)
    db_type = Column(String(20), nullable=False)
    host = Column(String(200), nullable=False)
    port = Column(Integer, nullable=False)
    database = Column(String(200), nullable=True)
    username = Column(String(200), nullable=False)
    password = Column(Text, nullable=False)

KST = pytz.timezone('Asia/Seoul')

class File(Base):
    __tablename__ = 'files'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    file_name = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    # uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(KST))
    file_data = Column(LONGBLOB, nullable=False)
    option = Column(String(255), index=True)
    summary_output = Column(Text, nullable=True)

# DB 테이블을 생성하는 함수 (main.py 등에서 앱 시작 시 호출)
def init_db():
    Base.metadata.create_all(bind=engine)
