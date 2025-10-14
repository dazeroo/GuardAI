import logging
from fastapi import APIRouter, HTTPException
from app.models.ai_models import GenerateRequest, GenerateResponse
from app.services.v2.ai_service import generate_ai_response

router = APIRouter()

# tech-ai 추가 진단
@router.post("/tech/ai", response_model=GenerateResponse)
async def run_ai(req: GenerateRequest):
    try:
        return await generate_ai_response(req)
    except Exception as e:
        # 에러 발생 시, 서버 로그에 자세한 내용을 기록합니다.
        # exc_info=True 옵션이 에러의 전체 추적 내용을 보여줍니다.
        logging.error("AI 진단 중 오류 발생:", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server Error: {e}")