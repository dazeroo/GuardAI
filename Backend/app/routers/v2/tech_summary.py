import io, json
from types import SimpleNamespace
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Form
from app.core.database import get_db
from app.models.models import File as DBFile
from app.services.v2.tech_summary_service import parse_report_auto

router = APIRouter()

@router.post("/summary")
async def summary(
    file_id: str = Form(...),
    domain: str = Form("WEB"),
    db: Session = Depends(get_db)
):
    """
    DB에 저장된 파일 ID를 기반으로 보고서를 분석(요약)합니다.
    """
    db_file = db.query(DBFile).filter(DBFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found in database")

    try:
        file_content = io.BytesIO(db_file.file_data)
        file_object_to_pass = SimpleNamespace(
            file=file_content, 
            filename=db_file.file_name
        )
        
        summary_output_list = parse_report_auto(file_object_to_pass, domain)
        summary_output_json_string = json.dumps(summary_output_list, indent=4, ensure_ascii=False)

        db_file.summary_output = summary_output_json_string
        db.commit()

        return summary_output_list

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred during analysis: {str(e)}")