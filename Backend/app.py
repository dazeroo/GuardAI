import os
import json
import asyncio
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai
import logging
import pandas as pd
import docx
from io import BytesIO

# .env 파일에서 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(title="ISMS-P 진단 API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini API 설정
try:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
    genai.configure(api_key=gemini_api_key)
    logger.info("Gemini API 설정 완료")
except Exception as e:
    logger.error(f"Gemini API 설정 중 오류 발생: {e}")

# [수정] ISMS-P 통제항목 101개를 파이썬 리스트로 정의 (Source of Truth)
ISMS_P_CONTROLS = [
    {"id": "1.1.1", "name": "경영진의 참여"}, {"id": "1.1.2", "name": "최고책임자의 지정"},
    {"id": "1.1.3", "name": "조직 구성"}, {"id": "1.1.4", "name": "범위 설정"},
    {"id": "1.1.5", "name": "정책 수립"}, {"id": "1.1.6", "name": "자원 할당"},
    {"id": "1.2.1", "name": "정보자산 식별"}, {"id": "1.2.2", "name": "현황 및 흐름분석"},
    {"id": "1.2.3", "name": "위험 평가"}, {"id": "1.2.4", "name": "보호대책 선정"},
    {"id": "1.3.1", "name": "보호대책 구현"}, {"id": "1.3.2", "name": "보호대책 공유"},
    {"id": "1.3.3", "name": "운영현황 관리"}, {"id": "1.4.1", "name": "법적 요구사항 준수 검토"},
    {"id": "1.4.2", "name": "관리체계 점검"}, {"id": "1.4.3", "name": "관리체계 개선"},
    {"id": "2.1.1", "name": "정책의 유지관리"}, {"id": "2.1.2", "name": "조직의 유지관리"},
    {"id": "2.1.3", "name": "정보자산 관리"}, {"id": "2.2.1", "name": "주요 직무자 지정 및 관리"},
    {"id": "2.2.2", "name": "직무 분리"}, {"id": "2.2.3", "name": "보안 서약"},
    {"id": "2.2.4", "name": "인식제고 및 교육훈련"}, {"id": "2.2.5", "name": "퇴직 및 직무변경 관리"},
    {"id": "2.2.6", "name": "보안 위반 시 조치"}, {"id": "2.3.1", "name": "외부자 현황 관리"},
    {"id": "2.3.2", "name": "외부자 계약 시 보안"}, {"id": "2.3.3", "name": "외부자 보안 이행 관리"},
    {"id": "2.3.4", "name": "외부자 계약 변경 및 만료 시 보안"}, {"id": "2.4.1", "name": "보호구역 지정"},
    {"id": "2.4.2", "name": "출입통제"}, {"id": "2.4.3", "name": "정보시스템 보호"},
    {"id": "2.4.4", "name": "보호설비 운영"}, {"id": "2.4.5", "name": "보호구역 내 작업"},
    {"id": "2.4.6", "name": "반출입 기기 통제"}, {"id": "2.4.7", "name": "업무환경 보안"},
    {"id": "2.5.1", "name": "사용자 계정 관리"}, {"id": "2.5.2", "name": "사용자 식별"},
    {"id": "2.5.3", "name": "사용자 인증"}, {"id": "2.5.4", "name": "비밀번호 관리"},
    {"id": "2.5.5", "name": "특수 계정 및 권한 관리"}, {"id": "2.5.6", "name": "접근권한 검토"},
    {"id": "2.6.1", "name": "네트워크 접근"}, {"id": "2.6.2", "name": "정보시스템 접근"},
    {"id": "2.6.3", "name": "응용프로그램 접근"}, {"id": "2.6.4", "name": "데이터베이스 접근"},
    {"id": "2.6.5", "name": "무선 네트워크 접근"}, {"id": "2.6.6", "name": "원격접근 통제"},
    {"id": "2.6.7", "name": "인터넷 접속 통제"}, {"id": "2.7.1", "name": "암호정책 적용"},
    {"id": "2.7.2", "name": "암호키 관리"}, {"id": "2.8.1", "name": "보안 요구사항 정의"},
    {"id": "2.8.2", "name": "보안 요구사항 검토 및 시험"}, {"id": "2.8.3", "name": "시험과 운영 환경 분리"},
    {"id": "2.8.4", "name": "시험 데이터 보안"}, {"id": "2.8.5", "name": "소스 프로그램 관리"},
    {"id": "2.8.6", "name": "운영환경 이관"}, {"id": "2.9.1", "name": "변경관리"},
    {"id": "2.9.2", "name": "성능 및 장애관리"}, {"id": "2.9.3", "name": "백업 및 복구관리"},
    {"id": "2.9.4", "name": "로그 및 접속기록 관리"}, {"id": "2.9.5", "name": "로그 및 접속기록 점검"},
    {"id": "2.9.6", "name": "시간 동기화"}, {"id": "2.9.7", "name": "정보자산의 재사용 및 폐기"},
    {"id": "2.10.1", "name": "보안시스템 운영"}, {"id": "2.10.2", "name": "클라우드 보안"},
    {"id": "2.10.3", "name": "공개서버 보안"}, {"id": "2.10.4", "name": "전자거래 및 핀테크 보안"},
    {"id": "2.10.5", "name": "정보전송 보안"}, {"id": "2.10.6", "name": "업무용 단말기기 보안"},
    {"id": "2.10.7", "name": "보조저장매체 관리"}, {"id": "2.10.8", "name": "패치관리"},
    {"id": "2.10.9", "name": "악성코드 통제"}, {"id": "2.11.1", "name": "사고 예방 및 대응체계 구축"},
    {"id": "2.11.2", "name": "취약점 점검 및 조치"}, {"id": "2.11.3", "name": "이상행위 분석 및 모니터링"},
    {"id": "2.11.4", "name": "사고 대응 훈련 및 개선"}, {"id": "2.11.5", "name": "사고 대응 및 복구"},
    {"id": "2.12.1", "name": "재해·재난 대비 안전조치"}, {"id": "2.12.2", "name": "재해 복구 시험 및 개선"},
    {"id": "3.1.1", "name": "개인정보 수집.이용"}, {"id": "3.1.2", "name": "개인정보의 수집 제한"},
    {"id": "3.1.3", "name": "주민등록번호 처리 제한"}, {"id": "3.1.4", "name": "민감정보 및 고유식별정보의 처리 제한"},
    {"id": "3.1.5", "name": "간접수집 보호조치"}, {"id": "3.1.6", "name": "영상정보처리기기 설치·운영"},
    {"id": "3.1.7", "name": "마케팅 목적의 개인정보 수집.이용"}, {"id": "3.2.1", "name": "개인정보 현황관리"},
    {"id": "3.2.2", "name": "개인정보 품질보장"}, {"id": "3.2.3", "name": "이용자 단말기 접근 보호"},
    {"id": "3.2.4", "name": "개인정보 목적 외 이용 및 제공"}, {"id": "3.2.5", "name": "가명정보 처리"},
    {"id": "3.3.1", "name": "개인정보 제3자 제공"}, {"id": "3.3.2", "name": "개인정보 처리 업무 위탁"},
    {"id": "3.3.3", "name": "영업의 양수 등에 따른 개인정보의 이전"}, {"id": "3.3.4", "name": "개인정보의 국외이전"},
    {"id": "3.4.1", "name": "개인정보의 파기"}, {"id": "3.4.2", "name": "처리목적 달성 후 보유 시 조치"},
    {"id": "3.5.1", "name": "개인정보처리방침 공개"}, {"id": "3.5.2", "name": "정보주체 권리보장"},
    {"id": "3.5.3", "name": "정보주체에 대한 통지"}
]

# [수정] 단일 항목을 비동기적으로 진단하는 함수
async def diagnose_item_async(item, guideline_text, model):
    """단일 ISMS-P 항목을 진단하는 비동기 함수"""
    try:
        # [수정] 매우 단순하고 명확한 프롬프트
        prompt = f"""
        당신은 ISMS-P 인증 심사 전문가입니다. 주어진 [회사 지침서] 내용을 보고, 아래 [평가 항목]을 만족하는지 평가해주세요.

        [회사 지침서]
        {guideline_text[:10000]}

        [평가 항목]
        - 항목 ID: {item['id']}
        - 항목명: {item['name']}

        [평가 기준]
        - 'Y'(양호): 지침서에 [평가 항목]에 대한 명확한 내용이 있음
        - 'P'(부분충족): 지침서에 일부 내용만 있거나 불완전함
        - 'N'(미흡): 지침서에 해당 내용이 없거나 매우 부족함

        [응답 형식]
        반드시 아래와 같은 JSON 형식으로만 응답해주세요. 다른 설명은 절대 추가하지 마세요.
        {{"rating": "Y/P/N 중 하나", "reason": "평가 근거를 2~3문장으로 요약"}}
        """

        generation_config = {"temperature": 0.1}
        
        response = await model.generate_content_async(prompt, generation_config=generation_config)
        
        response_text = response.text.strip()
        
        # AI 응답에서 JSON만 추출
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        
        # JSON 파싱
        diagnosis_result = json.loads(response_text)
        
        # 최종 결과 객체 생성
        return {
            "id": item["id"],
            "name": item["name"],
            "rating": diagnosis_result.get("rating", "N"),
            "reason": diagnosis_result.get("reason", "AI 응답 파싱 오류")
        }

    except Exception as e:
        logger.error(f"항목 {item['id']} 진단 중 오류: {e}")
        return {
            "id": item["id"],
            "name": item["name"],
            "rating": "N",
            "reason": f"진단 중 오류 발생: {e}"
        }

# 자동 진단 API 엔드포인트
@app.post("/api/diagnose")
async def diagnose(guideline: UploadFile = File(...)):
    if not guideline.filename:
        raise HTTPException(status_code=400, detail="파일이 선택되지 않았습니다.")

    try:
        file_content = await guideline.read()
        guideline_text = ""
        if guideline.filename.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(file_content), engine='openpyxl')
            guideline_text = ' '.join(df.astype(str).stack())
        elif guideline.filename.endswith('.docx'):
            doc = docx.Document(BytesIO(file_content))
            guideline_text = "\n".join([para.text for para in doc.paragraphs])
        else:
            guideline_text = file_content.decode('utf-8', errors='ignore')

        if not guideline_text.strip():
            raise HTTPException(status_code=400, detail="파일이 비어있습니다.")

        logger.info(f"파일 '{guideline.filename}' 처리 완료. Gemini API로 101개 항목 진단 시작...")

        # [수정] 비동기 처리를 위한 모델 생성
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # [수정] 101개 항목에 대한 비동기 작업 생성
        tasks = [diagnose_item_async(item, guideline_text, model) for item in ISMS_P_CONTROLS]
        
        # [수정] asyncio.gather를 사용하여 모든 작업을 동시에 실행
        diagnosis_results = await asyncio.gather(*tasks)
        
        logger.info(f"101개 항목 진단 완료. 결과 개수: {len(diagnosis_results)}")
        
        return diagnosis_results

    except Exception as e:
        logger.error(f"진단 프로세스 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="진단 보고서 생성 중 서버 오류가 발생했습니다.")


@app.get("/")
async def root():
    return {"status": "ok", "message": "ISMS-P 진단 API 서버가 정상 작동 중입니다."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
