from fastapi import APIRouter, HTTPException
from app.models.ai_models import GenerateRequest, GenerateResponse
from app.services.ai_service import generate_ai_response

router = APIRouter()

@router.post("/run", response_model=GenerateResponse)
async def run_ai(req: GenerateRequest):
    try:
        return await generate_ai_response(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {e}")
