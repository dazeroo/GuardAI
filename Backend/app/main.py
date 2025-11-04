import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()
import logging
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.models import init_db
from app.routers.v2 import items, targets, tech_summary, upload, ai, mng_auto_diagnose
from app.routers.v2.webscan import router as webscan_router

logger = logging.getLogger("uvicorn") 
app = FastAPI(title="GuardAI API")

@app.on_event("startup")
def on_startup():
    """
    FastAPI 애플리케이션 시작 시 DB 및 Gemini API 초기화
    """
    # 1. 데이터베이스 초기화
    logger.info("애플리케이션 시작... 데이터베이스 초기화를 진행합니다.")
    init_db()
    logger.info("데이터베이스 초기화 완료.")

    # 2. Gemini API 설정
    try:
        my_key = os.getenv("GENAI_API_KEY")
        logger.info(f"불러온 API KEY: {my_key}")
        if not my_key:
            raise ValueError("GENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        genai.configure(api_key=my_key)
        logger.info("Gemini API 설정이 완료되었습니다.")
    except Exception as e:
        logger.error(f"Gemini API 설정 중 오류 발생: {e}")
    
app.add_middleware(
    CORSMiddleware,
    #allow_origins=["*"],  # 개발 단계: 모두 허용, 운영에서는 도메인 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(items.router, prefix="/routers/v2", tags=["tech", "items"])
app.include_router(targets.router, prefix="/routers/v2", tags=["tech", "auto", "targets"])
app.include_router(tech_summary.router, prefix="/routers/v2", tags=["tech", "summary"])
app.include_router(upload.router, prefix="/routers/v2", tags=["tech", "summary", "upload"])
app.include_router(ai.router, prefix="/routers/v2", tags=["tech", "AI"])
app.include_router(mng_auto_diagnose.router, prefix="/routers/v2", tags=["mng", "auto"])
app.include_router(webscan_router, prefix="/api/v2", tags=["scan", "web"])

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="localhost", port=8080) # 사용중이라서 8080으로 옮김
