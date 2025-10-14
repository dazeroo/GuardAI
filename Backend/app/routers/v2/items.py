from fastapi import APIRouter
from app.services.v2.tech_summary_service import get_items

router = APIRouter()

@router.get("/tech/items")   
def get_items_endpoint():
    """
    analyzer.py에 정의된 DB 및 WEB 진단 항목 목록을 반환합니다.
    """
    return get_items()