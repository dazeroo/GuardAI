import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import logging
import pandas as pd
import docx
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app) 

try:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
    genai.configure(api_key=gemini_api_key)
except Exception as e:
    app.logger.error(f"Gemini API 설정 중 오류 발생: {e}")

# 101개 항목 정의
ISMS_P_CONTROLS = [
    "1.1.1 경영진의 참여", "1.1.2 최고책임자의 지정", "1.1.3 조직 구성", "1.1.4 범위 설정",
    "1.1.5 정책 수립", "1.1.6 자원 할당", "1.2.1 정보자산 식별", "1.2.2 현황 및 흐름분석",
    "1.2.3 위험 평가", "1.2.4 보호대책 선정", "1.3.1 보호대책 구현", "1.3.2 보호대책 공유",
    "1.3.3 운영현황 관리", "1.4.1 법적 요구사항 준수 검토", "1.4.2 관리체계 점검", "1.4.3 관리체계 개선",
    "2.1.1 정책의 유지관리", "2.1.2 조직의 유지관리", "2.1.3 정보자산 관리", "2.2.1 주요 직무자 지정 및 관리",
    "2.2.2 직무 분리", "2.2.3 보안 서약", "2.2.4 인식제고 및 교육훈련", "2.2.5 퇴직 및 직무변경 관리",
    "2.2.6 보안 위반 시 조치", "2.3.1 외부자 현황 관리", "2.3.2 외부자 계약 시 보안", "2.3.3 외부자 보안 이행 관리",
    "2.3.4 외부자 계약 변경 및 만료 시 보안", "2.4.1 보호구역 지정", "2.4.2 출입통제", "2.4.3 정보시스템 보호",
    "2.4.4 보호설비 운영", "2.4.5 보호구역 내 작업", "2.4.6 반출입 기기 통제", "2.4.7 업무환경 보안",
    "2.5.1 사용자 계정 관리", "2.5.2 사용자 식별", "2.5.3 사용자 인증", "2.5.4 비밀번호 관리",
    "2.5.5 특수 계정 및 권한 관리", "2.5.6 접근권한 검토", "2.6.1 네트워크 접근", "2.6.2 정보시스템 접근",
    "2.6.3 응용프로그램 접근", "2.6.4 데이터베이스 접근", "2.6.5 무선 네트워크 접근", "2.6.6 원격접근 통제",
    "2.6.7 인터넷 접속 통제", "2.7.1 암호정책 적용", "2.7.2 암호키 관리", "2.8.1 보안 요구사항 정의",
    "2.8.2 보안 요구사항 검토 및 시험", "2.8.3 시험과 운영 환경 분리", "2.8.4 시험 데이터 보안", "2.8.5 소스 프로그램 관리",
    "2.8.6 운영환경 이관", "2.9.1 변경관리", "2.9.2 성능 및 장애관리", "2.9.3 백업 및 복구관리",
    "2.9.4 로그 및 접속기록 관리", "2.9.5 로그 및 접속기록 점검", "2.9.6 시간 동기화", "2.9.7 정보자산의 재사용 및 폐기",
    "2.10.1 보안시스템 운영", "2.10.2 클라우드 보안", "2.10.3 공개서버 보안", "2.10.4 전자거래 및 핀테크 보안",
    "2.10.5 정보전송 보안", "2.10.6 업무용 단말기기 보안", "2.10.7 보조저장매체 관리", "2.10.8 패치관리",
    "2.10.9 악성코드 통제", "2.11.1 사고 예방 및 대응체계 구축", "2.11.2 취약점 점검 및 조치", "2.11.3 이상행위 분석 및 모니터링",
    "2.11.4 사고 대응 훈련 및 개선", "2.11.5 사고 대응 및 복구", "2.12.1 재해·재난 대비 안전조치", "2.12.2 재해 복구 시험 및 개선",
    "3.1.1 개인정보 수집.이용", "3.1.2 개인정보의 수집 제한", "3.1.3 주민등록번호 처리 제한", "3.1.4 민감정보 및 고유식별정보의 처리 제한",
    "3.1.5 간접수집 보호조치", "3.1.6 영상정보처리기기 설치·운영", "3.1.7 마케팅 목적의 개인정보 수집.이용", "3.2.1 개인정보 현황관리",
    "3.2.2 개인정보 품질보장", "3.2.3 이용자 단말기 접근 보호", "3.2.4 개인정보 목적 외 이용 및 제공", "3.2.5 가명정보 처리",
    "3.3.1 개인정보 제3자 제공", "3.3.2 개인정보 처리 업무 위탁", "3.3.3 영업의 양수 등에 따른 개인정보의 이전", "3.3.4 개인정보의 국외이전",
    "3.4.1 개인정보의 파기", "3.4.2 처리목적 달성 후 보유 시 조치", "3.5.1 개인정보처리방침 공개", "3.5.2 정보주체 권리보장",
    "3.5.3 정보주체에 대한 통지"
]

def create_optimized_prompt(guideline_text, batch_items):
    """최적화된 프롬프트 생성"""
    items_str = "\n".join([f"- {item}" for item in batch_items])
    truncated_text = guideline_text[:20000]  # 20,000자로 제한
    
    return f"""ISMS-P 인증 심사 전문가로서 지침서를 분석하세요.

[평가 항목]
{items_str}

[평가 기준]
Y: 명확한 내용 있음 | P: 일부만 있음 | N: 내용 없음

[응답] JSON 배열만 출력:
[
  {{"id": "1.1.1", "name": "경영진의 참여", "rating": "Y", "reason": "간결한 평가"}},
  ...
]

[지침서]
{truncated_text}
"""

@app.route("/api/diagnose", methods=["POST"])
def diagnose():
    if 'guideline' not in request.files:
        return jsonify({"error": "파일이 업로드되지 않았습니다."}), 400

    file = request.files['guideline']
    if file.filename == '':
        return jsonify({"error": "파일이 선택되지 않았습니다."}), 400
    
    try:
        guideline_text = ""
        
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(file, engine='openpyxl')
            guideline_text = ' '.join(df.astype(str).stack())
        elif file.filename.endswith('.docx'):
            doc = docx.Document(file)
            guideline_text = "\n".join([para.text for para in doc.paragraphs])
        else:
            guideline_text = file.read().decode('utf-8', errors='ignore')

        if not guideline_text.strip():
            return jsonify({"error": "파일이 비어있습니다."}), 400

        app.logger.info(f"파일 '{file.filename}' 처리 완료 (길이: {len(guideline_text)})")
        
        # 3개 배치로 분할
        batch_1 = ISMS_P_CONTROLS[:34]
        batch_2 = ISMS_P_CONTROLS[34:68]
        batch_3 = ISMS_P_CONTROLS[68:]
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        app.logger.info("3개 배치로 병렬 처리 시작...")
        
        def process_batch(batch_items, batch_num):
            try:
                app.logger.info(f"배치 {batch_num} 시작 ({len(batch_items)}개)")
                prompt = create_optimized_prompt(guideline_text, batch_items)
                
                response = model.generate_content(
                    prompt,
                    generation_config={"temperature": 0.1, "max_output_tokens": 8192}
                )
                
                # ★ 핵심: finish_reason 먼저 체크
                if not response.candidates or response.candidates[0].finish_reason != 1:
                    reason = response.candidates[0].finish_reason if response.candidates else "unknown"
                    app.logger.error(f"배치 {batch_num} 비정상 종료: finish_reason={reason}")
                    return [{"id": item.split()[0], "name": item.split(maxsplit=1)[1], 
                            "rating": "N", "reason": "AI 응답 생성 실패"} 
                            for item in batch_items]
                
                response_text = response.text.strip()
                
                if '```json' in response_text:
                    response_text = response_text.split('```json')[1].split('```')[0].strip()
                
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                
                if json_start != -1 and json_end > 0:
                    json_response = response_text[json_start:json_end]
                    result = json.loads(json_response)
                    app.logger.info(f"배치 {batch_num} 완료 ({len(result)}개)")
                    return result
                else:
                    app.logger.error(f"배치 {batch_num} JSON 파싱 실패")
                    return [{"id": item.split()[0], "name": item.split(maxsplit=1)[1], 
                            "rating": "N", "reason": "응답 파싱 실패"} 
                            for item in batch_items]
            
            except Exception as e:
                app.logger.error(f"배치 {batch_num} 오류: {str(e)[:100]}")
                return [{"id": item.split()[0], "name": item.split(maxsplit=1)[1], 
                        "rating": "N", "reason": "처리 오류"} 
                        for item in batch_items]
        
        # 병렬 처리
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_1 = executor.submit(process_batch, batch_1, 1)
            future_2 = executor.submit(process_batch, batch_2, 2)
            future_3 = executor.submit(process_batch, batch_3, 3)
            
            result_1 = future_1.result()
            result_2 = future_2.result()
            result_3 = future_3.result()
        
        all_results = result_1 + result_2 + result_3
        
        app.logger.info(f"전체 완료: {len(all_results)}/101개 항목")
        
        if len(all_results) != 101:
            app.logger.warning(f"결과 개수 불일치: {len(all_results)}/101")
        
        return jsonify(all_results)

    except Exception as e:
        app.logger.error(f"진단 중 오류: {e}", exc_info=True)
        return jsonify({"error": "진단 중 오류가 발생했습니다."}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3001, debug=True)
