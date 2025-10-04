from enum import Enum
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, SecretStr, HttpUrl

# Pydantic 모델(스키마) 정의
class DBType(str, Enum):
    mysql="mysql"; postgres="postgres"; mssql="mssql"

class DBCredIn(BaseModel):
    db_type: DBType
    host: str
    port: int
    database: Optional[str] = None
    username: str
    password: SecretStr

class DBCredOut(BaseModel):
    cred_id: str

class SiteIn(BaseModel):
    url: HttpUrl

class SiteOut(BaseModel):
    site_id: str

class FileIn(BaseModel):
    file_name: str
    content_type: str
    file_size: int
    
class FileOut(BaseModel):
    file_id: str
    file_name: str
    uploaded_at: datetime
    
    # Pydantic v2 호환성을 위해 orm_mode 대신 from_attributes 사용
    class Config:
        from_attributes = True