from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict

# 🌟 중요: WEB_Scanner/main.py 파일에서 run_scan 함수를 임포트합니다. 🌟
# app/routers/webscan.py에서 상위 두 단계(../..)로 이동 후, WEB_Scanner 폴더로 진입합니다.
try:
    from WEB_scanner.main import run_scan
except ImportError as e:
    # 경로 문제 발생 시 디버깅을 위해 에러를 출력할 수 있습니다.
    print(f"WEB_Scanner import 오류: {e}")
    # 실제 운영 환경에서는 적절한 오류 처리가 필요합니다.
    
    # 임시 Mock 함수 (실제 스캐너를 연결하기 전 테스트용)
    def run_scan(target_url, selected_tests=None):
        return {"error": "스캐너 로직을 찾을 수 없음"}, "{}", "<html><body></body></html>"


# 1. 요청 데이터를 정의하는 Pydantic 모델
class ScanRequest(BaseModel):
    url: str
    # 만약 프론트엔드에서 특정 검사 항목을 선택한다면 list[int] 타입의 필드를 추가할 수 있습니다.
    # selected_tests: list[int] | None = None 

# 2. 라우터 객체 생성
router = APIRouter()


# 3. API 엔드포인트 정의
@router.post("/scan")
async def start_web_scan(request: ScanRequest) -> Dict[str, Any]:
    """URL을 입력받아 취약점 스캔을 시작하고 결과를 반환하는 API."""
    target_url = request.url
    
    if not target_url:
        return {"status": "error", "message": "URL을 입력해야 합니다."}
    
    print(f"웹 진단 요청 접수: {target_url}")

    try:
        # run_scan 함수 호출 (선택된 테스트는 현재는 None으로 전체 실행)
        # run_scan은 (results, json_report, html_report)를 반환합니다.
        results, json_report, html_report = run_scan(target_url, selected_tests=None)
        
        # ⚠️ 경고: run_scan은 동기적이며 시간이 오래 걸립니다. 서버가 멈춥니다.
        # 비동기 처리는 별도의 고급 구현이 필요합니다.
        
        # 프론트엔드에 전달할 핵심 정보만 반환 (results 딕셔너리)
        return {
            "status": "success",
            "message": "웹 스캔이 성공적으로 완료되었습니다.",
            "report_summary": results,  # 각 테스트 결과 (취약/양호/인터뷰 등)
            "json_report": json_report, # (선택 사항) JSON 문자열 리포트
        }
    except Exception as e:
        # 스캐너 내부 오류 처리
        return {
            "status": "error",
            "message": f"웹 스캔 실행 중 치명적인 오류 발생: {str(e)}",
            "report_summary": None
        }
