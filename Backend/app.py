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
        아래 제공되는 회사의 내부 지침서 내용을 분석하여, ISMS-P의 모든 통제 항목(1.1.1부터 3.5.3까지 총 101개)을 만족하는지 진단해주세요.

        **매우 중요한 지시사항:**
        1.  **반드시 ISMS-P 통제항목 1.1.1부터 3.5.3까지 101개 전체에 대해 순서대로 빠짐없이 평가해야 합니다.**
        2.  각 항목의 id, name, rating, reason은 해당 항목에 대한 독립적인 분석 결과여야 합니다.
        3.  reason 내용은 다른 항목과 절대 섞이지 않도록 주의하세요.

        **평가 기준:**
        - 'Y'(양호): 지침서에 해당 항목에 대한 명확한 내용이 있음
        - 'P'(부분충족): 지침서에 일부 내용만 있거나 불완전함
        - 'N'(미흡): 지침서에 해당 항목에 대한 내용이 없거나 매우 부족함

        **reason 작성 규칙:**
        - 지침서에 내용이 없는 경우: "지침서에 [항목명]에 대한 내용이 명시되어 있지 않음" 이라고 작성하세요.
        - 그 외의 경우, 평가에 대한 구체적인 근거를 지침서 내용 기반으로 간결하게 작성하세요.

        **출력 형식:**
        - 다른 설명 없이, 오직 JSON 배열 형식으로만 응답해야 합니다.
        - 배열에는 정확히 101개의 JSON 객체가 포함되어야 합니다.
        - 최종 출력은 `[ {{"id": "1.1.1", ...}}, {{"id": "1.1.2", ...}}, ... ]` 형태의 순수한 JSON 배열이어야 합니다.

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
        # --- [OPTIMIZED] 안정성 설정 추가 ---
        # 유해성 판단 기준을 완화하여 부당하게 응답이 차단되는 경우를 줄입니다.
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

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
