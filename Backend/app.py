import os
import json
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
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한하세요
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


# 자동 진단 API 엔드포인트
@app.post("/api/diagnose")
async def diagnose(guideline: UploadFile = File(...)):
    """
    ISMS-P 자동 진단 API
    
    - **guideline**: 진단할 지침서 파일 (.xlsx, .docx, .txt)
    """
    
    # 파일 이름 확인
    if not guideline.filename:
        logger.warning("빈 파일 이름이 제출되었습니다.")
        raise HTTPException(status_code=400, detail="파일이 선택되지 않았습니다.")
    
    try:
        guideline_text = ""
        file_content = await guideline.read()
        
        # 파일 형식에 따른 처리
        if guideline.filename.endswith('.xlsx'):
            logger.info("엑셀 파일로 처리 시작")
            # pandas를 사용해 엑셀 파일의 모든 데이터를 읽어옴
            df = pd.read_excel(BytesIO(file_content), engine='openpyxl')
            # 엑셀의 모든 셀 내용을 하나의 긴 텍스트로 합침
            guideline_text = ' '.join(df.astype(str).stack())
            
        elif guideline.filename.endswith('.docx'):
            logger.info("워드 문서(.docx) 파일로 처리 시작")
            doc = docx.Document(BytesIO(file_content))
            guideline_text = "\n".join([para.text for para in doc.paragraphs])
            
        else:
            logger.info("일반 텍스트 파일로 처리 시작")
            # 텍스트 파일인 경우, 오류를 무시하고 UTF-8로 디코딩
            guideline_text = file_content.decode('utf-8', errors='ignore')

        if not guideline_text.strip():
            logger.warning("파일이 비어있거나 읽을 수 있는 텍스트가 없습니다.")
            raise HTTPException(status_code=400, detail="파일이 비어있거나 읽을 수 있는 텍스트가 없습니다.")

        logger.info(f"파일 '{guideline.filename}' 읽기 완료, 내용 길이: {len(guideline_text)}")
        
        # Gemini API에 보낼 프롬프트 정의
        prompt = f"""
        당신은 ISMS-P 인증 심사 전문가입니다.
        아래에 제공되는 회사의 내부 지침서 내용을 분석하여, ISMS-P의 각 통제 항목을 만족하는지 진단해주세요.
        
        ★★★ 매우 중요한 지시사항 ★★★
        1. 반드시 101개 항목 전체에 대해 순서대로 응답하세요.
        2. 각 항목의 id, name, rating, reason은 반드시 해당 항목에만 해당하는 내용이어야 합니다.
        3. reason 내용이 다른 항목과 섞이지 않도록 각 항목을 독립적으로 평가하세요.
        
        **평가 기준:**
        - 'Y'(양호): 지침서에 해당 항목에 대한 명확한 내용이 있음
        - 'P'(부분충족): 지침서에 일부 내용만 있거나 불완전함
        - 'N'(미흡): 지침서에 해당 항목에 대한 내용이 없거나 매우 부족함
        
        **reason 작성 규칙:**
        - 반드시 해당 항목 ID와 name에 직접적으로 관련된 내용만 작성
        - 다른 항목의 내용을 절대 포함하지 말 것
        - 지침서에 내용이 없으면: "지침서에 [항목명]에 대한 내용이 명시되어 있지 않음"
        
        **101개 항목 목록 (반드시 이 순서대로):**
        
        1.1.1 경영진의 참여
        1.1.2 최고책임자의 지정
        1.1.3 조직 구성
        1.1.4 범위 설정
        1.1.5 정책 수립
        1.1.6 자원 할당
        1.2.1 정보자산 식별
        1.2.2 현황 및 흐름분석
        1.2.3 위험 평가
        1.2.4 보호대책 선정
        1.3.1 보호대책 구현
        1.3.2 보호대책 공유
        1.3.3 운영현황 관리
        1.4.1 법적 요구사항 준수 검토
        1.4.2 관리체계 점검
        1.4.3 관리체계 개선
        2.1.1 정책의 유지관리
        2.1.2 조직의 유지관리
        2.1.3 정보자산 관리
        2.2.1 주요 직무자 지정 및 관리
        2.2.2 직무 분리
        2.2.3 보안 서약
        2.2.4 인식제고 및 교육훈련
        2.2.5 퇴직 및 직무변경 관리
        2.2.6 보안 위반 시 조치
        2.3.1 외부자 현황 관리
        2.3.2 외부자 계약 시 보안
        2.3.3 외부자 보안 이행 관리
        2.3.4 외부자 계약 변경 및 만료 시 보안
        2.4.1 보호구역 지정
        2.4.2 출입통제
        2.4.3 정보시스템 보호
        2.4.4 보호설비 운영
        2.4.5 보호구역 내 작업
        2.4.6 반출입 기기 통제
        2.4.7 업무환경 보안
        2.5.1 사용자 계정 관리
        2.5.2 사용자 식별
        2.5.3 사용자 인증
        2.5.4 비밀번호 관리
        2.5.5 특수 계정 및 권한 관리
        2.5.6 접근권한 검토
        2.6.1 네트워크 접근
        2.6.2 정보시스템 접근
        2.6.3 응용프로그램 접근
        2.6.4 데이터베이스 접근
        2.6.5 무선 네트워크 접근
        2.6.6 원격접근 통제
        2.6.7 인터넷 접속 통제
        2.7.1 암호정책 적용
        2.7.2 암호키 관리
        2.8.1 보안 요구사항 정의
        2.8.2 보안 요구사항 검토 및 시험
        2.8.3 시험과 운영 환경 분리
        2.8.4 시험 데이터 보안
        2.8.5 소스 프로그램 관리
        2.8.6 운영환경 이관
        2.9.1 변경관리
        2.9.2 성능 및 장애관리
        2.9.3 백업 및 복구관리
        2.9.4 로그 및 접속기록 관리
        2.9.5 로그 및 접속기록 점검
        2.9.6 시간 동기화
        2.9.7 정보자산의 재사용 및 폐기
        2.10.1 보안시스템 운영
        2.10.2 클라우드 보안
        2.10.3 공개서버 보안
        2.10.4 전자거래 및 핀테크 보안
        2.10.5 정보전송 보안
        2.10.6 업무용 단말기기 보안
        2.10.7 보조저장매체 관리
        2.10.8 패치관리
        2.10.9 악성코드 통제
        2.11.1 사고 예방 및 대응체계 구축
        2.11.2 취약점 점검 및 조치
        2.11.3 이상행위 분석 및 모니터링
        2.11.4 사고 대응 훈련 및 개선
        2.11.5 사고 대응 및 복구
        2.12.1 재해·재난 대비 안전조치
        2.12.2 재해 복구 시험 및 개선
        3.1.1 개인정보 수집.이용
        3.1.2 개인정보의 수집 제한
        3.1.3 주민등록번호 처리 제한
        3.1.4 민감정보 및 고유식별정보의 처리 제한
        3.1.5 간접수집 보호조치
        3.1.6 영상정보처리기기 설치·운영
        3.1.7 마케팅 목적의 개인정보 수집.이용
        3.2.1 개인정보 현황관리
        3.2.2 개인정보 품질보장
        3.2.3 이용자 단말기 접근 보호
        3.2.4 개인정보 목적 외 이용 및 제공
        3.2.5 가명정보 처리
        3.3.1 개인정보 제3자 제공
        3.3.2 개인정보 처리 업무 위탁
        3.3.3 영업의 양수 등에 따른 개인정보의 이전
        3.3.4 개인정보의 국외이전
        3.4.1 개인정보의 파기
        3.4.2 처리목적 달성 후 보유 시 조치
        3.5.1 개인정보처리방침 공개
        3.5.2 정보주체 권리보장
        3.5.3 정보주체에 대한 통지

          예시:
          {{"id": "2.6.4", "name": "데이터베이스 접근", "rating": "N", "reason": "데이터베이스 접근 통제 관련 내용..."}}
          {{"id": "2.7.1", "name": "암호정책 적용", "rating": "N", "reason": "암호화 정책 관련 내용..."}}
            
          절대로 reason 내용을 다른 항목과 섞지 마세요.

          결과는 반드시 아래와 같은 JSON 형식으로만 응답해야 합니다.
          **배열에는 정확히 101개의 객체가 포함되어야 합니다.**


          [JSON 응답 형식]
          [
            {{"id": "1.1.1", "name": "경영진의 참여", "rating": "Y/P/N", "reason": "평가 근거"}},
            {{"id": "1.1.2", "name": "최고책임자의 지정", "rating": "Y/P/N", "reason": "평가 근거"}},
            ...
            {{"id": "3.5.3", "name": "정보주체에 대한 통지", "rating": "Y/P/N", "reason": "평가 근거"}}
          ]

          ---
          [회사 내부 지침서 내용]
          {guideline_text}
          ---
        """
        
        logger.info("Gemini API 호출 시작")
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        response_text = response.text
        
        logger.info("Gemini API 응답 수신 완료")

        # 생성된 텍스트에서 JSON 부분만 추출
        # 마크다운 코드 블록(` ```json ... ``` `)을 제거
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        
        json_start = response_text.find('[')
        json_end = response_text.rfind(']') + 1
        
        if json_start == -1 or json_end == 0:
            logger.error("API 응답에서 유효한 JSON 배열을 찾지 못했습니다.")
            logger.debug(f"전체 응답 텍스트: {response_text}")
            raise HTTPException(status_code=500, detail="진단 결과에서 유효한 형식을 찾지 못했습니다.")
            
        json_response = response_text[json_start:json_end]
        
        # JSON 파싱 및 클라이언트에 전송
        diagnosis_data = json.loads(json_response)
        logger.info("JSON 파싱 성공, 클라이언트에 데이터 전송")
        return diagnosis_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"진단 보고서 생성 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="진단 보고서 생성 중 서버 오류가 발생했습니다.")


# 헬스체크 엔드포인트
@app.get("/")
async def root():
    """서버 상태 확인"""
    return {"status": "ok", "message": "ISMS-P 진단 API 서버가 정상 작동 중입니다."}


# 서버 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
