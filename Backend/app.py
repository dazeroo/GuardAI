import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

# .env 파일에서 환경 변수 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__)
# CORS 설정 (React 앱의 주소를 명시하는 것이 더 안전합니다)
CORS(app) 

# Gemini API 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
#model = genai.GenerativeModel('gemini-1.5-pro-latest')

# 자동 진단 API 엔드포인트
@app.route("/api/diagnose", methods=["POST"])
def diagnose():
    # 파일이 요청에 포함되어 있는지 확인
    if 'guideline' not in request.files:
        return jsonify({"error": "파일이 업로드되지 않았습니다."}), 400

    file = request.files['guideline']
    
    try:
        # 업로드된 파일의 내용을 텍스트로 변환
        guideline_text = file.read().decode('utf-8')

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
        
        # Gemini API 호출
        response = genai.generate_text(
        model='models/gemini-1.5-pro-latest', # 모델 이름 앞에 'models/'가 붙습니다.
        prompt=prompt,
        temperature=0.7 # 필요한 경우 다른 파라미터 추가
        )
        
        # 생성된 텍스트에서 JSON 부분만 추출
        response_text = response.result
        json_start = response_text.find('[')
        json_end = response_text.rfind(']') + 1
        json_response = response_text[json_start:json_end]
        
        # JSON 파싱 및 클라이언트에 전송
        diagnosis_data = json.loads(json_response)
        return jsonify(diagnosis_data)

    except Exception as e:
        print(f"오류 발생: {e}")
        return jsonify({"error": "진단 보고서 생성 중 오류가 발생했습니다."}), 500

# 서버 실행
if __name__ == "__main__":
    app.run(port=3001, debug=True)
