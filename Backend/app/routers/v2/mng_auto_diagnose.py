import logging
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.v2.mng_auto_diagnose_service import analyze_guideline

logger = logging.getLogger(__name__)

router = APIRouter()

# mng 자동 진단 API 엔드포인트
@router.post("/mng/auto/diagnose", summary="ISMS-P 자동 진단")
async def diagnose_guideline(guideline: UploadFile = File(...)):
    """
    업로드된 지침서 파일(xlsx, docx, txt)을 분석하여
    ISMS-P 통제 항목 준수 여부를 진단합니다.
    """
    if not guideline.filename:
        raise HTTPException(status_code=400, detail="파일이 선택되지 않았습니다.")

    try:
        # 1. HTTP 요청으로부터 파일 내용을 읽음
        content_bytes = await guideline.read()
        
        # 2. 서비스 계층의 함수를 호출하여 비즈니스 로직 처리
        diagnosis_result = await analyze_guideline(
            filename=guideline.filename,
            content_bytes=content_bytes
        )
        
        # 3. 처리 결과를 클라이언트에 반환
        return diagnosis_result

    except ValueError as e:
        # 서비스에서 발생시킨 특정 오류(ValueError)는 클라이언트의 잘못일 가능성이 높음
        logger.warning(f"클라이언트 요청 오류: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 그 외의 모든 오류는 서버 내부 문제로 처리
        logger.error(f"진단 API 처리 중 서버 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="진단 보고서 생성 중 서버 오류가 발생했습니다.")
