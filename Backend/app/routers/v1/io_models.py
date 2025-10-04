# app/api/v1/io_models.py
from pydantic import BaseModel, Field, SecretStr, HttpUrl
from enum import Enum
from typing import Optional
from uuid import uuid4
from datetime import datetime

class DBType(str, Enum):
    mysql="mysql"; postgres="postgres"; mssql="mssql"

class DBCredIn(BaseModel):
    db_type: DBType
    host: str
    port: int
    database: str
    username: str
    password: SecretStr

class DBCredOut(BaseModel):
    cred_id: str

class SiteIn(BaseModel):
    url: HttpUrl

class SiteOut(BaseModel):
    site_id: str


# 파일 메타데이터 모델 추가
class FileIn(BaseModel):
    file_name: str
    content_type: str
    file_size: int
    
class FileOut(BaseModel):
    file_id: str
    file_name: str
    uploaded_at: datetime
