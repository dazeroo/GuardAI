from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import report
from app.api.v1.io_store import router as store_router

app = FastAPI(title="Security Report API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계: 모두 허용, 운영에서는 도메인 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(report.router, prefix="/api/v1")
app.include_router(store_router, prefix="/api/v1")