from uuid import uuid4
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, UploadFile
from app.core.database import get_db
from app.schemas.schemas import FileOut
from app.models.models import File

router = APIRouter(tags=["store"])

@router.post("/files/upload", response_model=FileOut)
async def upload_file(
    file: UploadFile,
    db: Session = Depends(get_db)
):
    file_contents = await file.read()
    file_size = len(file_contents)
    file_id = str(uuid4())

    db_file = File(
        id=file_id,
        file_name=file.filename,
        content_type=file.content_type,
        file_size=file_size,
        file_data=file_contents
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return FileOut(
        file_id=db_file.id,
        file_name=db_file.file_name,
        uploaded_at=db_file.uploaded_at
    )