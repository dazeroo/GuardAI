import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import logging
import pandas as pd
import docx

# .env 파일에서 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# Flask 앱 초기화
app = Flask(__name__)
# CORS 설정 (React 앱의 주소를 명시하는 것이 더 안전합니다)
CORS(app) 

# Gemini API 설정
try:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
    genai.configure(api_key=gemini_api_key)
except Exception as e:
    app.logger.error(f"Gemini API 설정 중 오류 발생: {e}")

# 자동 진단 API 엔드포인트
@app.route("/api/diagnose", methods=["POST"])
def diagnose():
    # 파일이 요청에 포함되어 있는지 확인
    if 'guideline' not in request.files:
        app.logger.warning("파일이 업로드되지 않았습니다.")
        return jsonify({"error": "파일이 업로드되지 않았습니다."}), 400

    file = request.files['guideline']

    if file.filename == '':
        app.logger.warning("빈 파일 이름이 제출되었습니다.")
        return jsonify({"error": "파일이 선택되지 않았습니다."}), 400
    
    try:
        guideline_text = ""
        # 파일 이름이 .xlsx로 끝나는지 확인하여 엑셀 파일인지 판별
        if file.filename.endswith('.xlsx'):
            app.logger.info("엑셀 파일로 처리 시작")
            # pandas를 사용해 엑셀 파일의 모든 데이터를 읽어옴
            df = pd.read_excel(file, engine='openpyxl')
            # 엑셀의 모든 셀 내용을 하나의 긴 텍스트로 합침
            guideline_text = ' '.join(df.astype(str).stack())
        elif file.filename.endswith('.docx'):
              app.logger.info("워드 문서(.docx) 파일로 처리 시작")
              doc = docx.Document(file)
              guideline_text = "\n".join([para.text for para in doc.paragraphs])
        else:
            app.logger.info("일반 텍스트 파일로 처리 시작")
            # 텍스트 파일인 경우, 오류를 무시하고 UTF-8로 디코딩
            guideline_text = file.read().decode('utf-8', errors='ignore')

        if not guideline_text.strip():
            app.logger.warning("파일이 비어있거나 읽을 수 있는 텍스트가 없습니다.")
            return jsonify({"error": "파일이 비어있거나 읽을 수 있는 텍스트가 없습니다."}), 400

        app.logger.info(f"파일 '{file.filename}' 읽기 완료, 내용 길이: {len(guideline_text)}")
        
        # Gemini API에 보낼 프롬프트 정의 (Express 예제와 동일)
        prompt = f"""
          당신은 ISMS-P 인증 심사 전문가입니다.
          아래에 제공되는 회사의 내부 지침서 내용을 분석하여, ISMS-P의 각 통제 항목을 만족하는지 진단해주세요.

          결과는 반드시 아래와 같은 JSON 형식으로만 응답해야 합니다.
          각 항목에 대한 진단 결과는 'Y'(양호), 'P'(부분충족), 'N'(미흡) 중 하나로 평가하고, 평가에 대한 구체적인 근거를 지침서 내용에 기반하여 간결하게 작성해주세요.
          만약 지침서 내용에서 판단 근거를 찾을 수 없다면, '판단 불가' 또는 '관련 내용 없음'으로 명시해주세요.

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
        
        app.logger.info("Gemini API 호출 시작")
        
        model = genai.GenerativeModel('gemini-1.0-pro')
        response = model.generate_content(prompt)
        response_text = response.text
        
        app.logger.info("Gemini API 응답 수신 완료")

        # 생성된 텍스트에서 JSON 부분만 추출
        # 마크다운 코드 블록(` ```json ... ``` `)을 제거
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        
        json_start = response_text.find('[')
        json_end = response_text.rfind(']') + 1
        
        if json_start == -1 or json_end == 0:
            app.logger.error("API 응답에서 유효한 JSON 배열을 찾지 못했습니다.")
            app.logger.debug(f"전체 응답 텍스트: {response_text}")
            return jsonify({"error": "진단 결과에서 유효한 형식을 찾지 못했습니다."}), 500
            
        json_response = response_text[json_start:json_end]
        
        # JSON 파싱 및 클라이언트에 전송
        diagnosis_data = json.loads(json_response)
        app.logger.info("JSON 파싱 성공, 클라이언트에 데이터 전송")
        return jsonify(diagnosis_data)

    except Exception as e:
        app.logger.error(f"진단 보고서 생성 중 오류 발생: {e}", exc_info=True)
        return jsonify({"error": "진단 보고서 생성 중 서버 오류가 발생했습니다."}), 500

# 서버 실행
if __name__ == "__main__":
    # 0.0.0.0으로 호스트를 설정하여 외부에서도 접속 가능하도록 함
    app.run(host='0.0.0.0', port=3001, debug=True)
