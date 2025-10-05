import os
import json
import logging
import google.generativeai as genai
import pandas as pd
import docx
import io

logger = logging.getLogger(__name__)

async def analyze_guideline(filename: str, content_bytes: bytes) -> list:
    """
    파일명과 파일 내용을 받아 ISMS-P 진단을 수행하고 결과를 반환합니다.
    """
    try:
        guideline_text = ""
        # 파일 확장자에 따라 텍스트 추출
        if filename.endswith('.xlsx'):
            logger.info("엑셀 파일로 처리 시작")
            df = pd.read_excel(io.BytesIO(content_bytes), engine='openpyxl')
            guideline_text = ' '.join(df.astype(str).stack())
        elif filename.endswith('.docx'):
            logger.info("워드 문서(.docx) 파일로 처리 시작")
            doc = docx.Document(io.BytesIO(content_bytes))
            guideline_text = "\n".join([para.text for para in doc.paragraphs])
        else:
            logger.info("일반 텍스트 파일로 처리 시작")
            guideline_text = content_bytes.decode('utf-8', errors='ignore')

        if not guideline_text.strip():
            logger.warning("파일이 비어있거나 읽을 수 있는 텍스트가 없습니다.")
            # 서비스단에서는 구체적인 에러를 발생시켜 라우터가 처리하도록 함
            raise ValueError("파일이 비어있거나 읽을 수 있는 텍스트가 없습니다.")

        logger.info(f"파일 '{filename}' 읽기 완료, 내용 길이: {len(guideline_text)}")

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
        ... (중략) ...
        3.5.3 정보주체에 대한 통지

        결과는 반드시 아래와 같은 JSON 형식으로만 응답해야 합니다.
        **배열에는 정확히 101개의 객체가 포함되어야 합니다.**

        [JSON 응답 형식]
        [
          {{"id": "1.1.1", "name": "경영진의 참여", "rating": "Y/P/N", "reason": "평가 근거"}},
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
        response = await model.generate_content_async(prompt)
        response_text = response.text
        logger.info("Gemini API 응답 수신 완료")

        # 응답 텍스트에서 JSON 부분만 정제
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        
        json_start = response_text.find('[')
        json_end = response_text.rfind(']') + 1
        
        if json_start == -1 or json_end == 0:
            logger.error("API 응답에서 유효한 JSON 배열을 찾지 못했습니다.")
            raise ValueError("진단 결과에서 유효한 형식을 찾지 못했습니다.")
            
        json_response_str = response_text[json_start:json_end]
        
        diagnosis_data = json.loads(json_response_str)
        logger.info("JSON 파싱 성공")
        return diagnosis_data

    except Exception as e:
        logger.error(f"서비스 로직 처리 중 오류 발생: {e}", exc_info=True)
        # 발생한 에러를 그대로 다시 발생시켜 라우터에서 처리하도록 함
        raise e