# app/api/v1/report.py
from fastapi import APIRouter, Depends, HTTPException, File, Form
from sqlalchemy.orm import Session
from app.services.analyzer import parse_report_auto
from app.api.v1.io_store import File as DBFile, get_db  # File 모델과 get_db 의존성 주입 함수를 가져옵니다.
import os
import io

# 파일이 저장된 디렉터리 경로를 정의합니다.
# 이 경로는 io_store.py의 UPLOAD_DIRECTORY와 동일해야 합니다.
UPLOAD_DIRECTORY = "./reports"

router = APIRouter(prefix="/analyze-report", tags=["report"])

@router.post("")
async def analyze_report(
    file_id: str = Form(...),  # Form 데이터로 파일 ID를 받습니다.
    domain: str = Form("WEB"),
    db: Session = Depends(get_db)  # DB 세션 의존성 주입
):
    """
    업로드된 파일 ID를 기반으로 보고서를 분석합니다.
    """
    # 1. DB에서 파일 메타데이터 조회
    db_file = db.query(DBFile).filter(DBFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # 2. 파일 시스템에서 실제 파일 경로를 찾아 파일을 읽습니다.
    file_path = os.path.join(UPLOAD_DIRECTORY, f"{db_file.id}_{db_file.file_name}")
    
    # 파일이 실제로 존재하는지 확인
    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="Stored file not found on server.")

    try:
        # 파일 내용을 바이트 스트림으로 읽어 FastAPI의 UploadFile 객체처럼 시뮬레이션합니다.
        # 이렇게 해야 parse_report_auto 함수가 기존과 동일하게 동작합니다.
        with open(file_path, "rb") as f:
            file_content = io.BytesIO(f.read())
            
        file_obj = UploadFile(
            file=file_content,
            filename=db_file.file_name,
            content_type=db_file.content_type
        )
        
        # 3. 분석기 호출
        items = parse_report_auto(file_obj, domain)
        return {"items": items}

    except Exception as e:
        # 예상치 못한 오류 발생 시 500 에러 반환
        raise HTTPException(status_code=500, detail=f"An error occurred during analysis: {str(e)}")
