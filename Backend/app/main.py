from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.v1 import ai
# from app.api.v1 import report
# from app.api.v1.io_store import router as store_router

app = FastAPI(title="GuardAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계: 모두 허용, 운영에서는 도메인 제한 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
# app.include_router(report.router, prefix="/api/v1")
# app.include_router(store_router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8080) # 사용중이라서 8080으로 옮김