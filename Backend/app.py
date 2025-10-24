import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import logging
import pandas as pd
import docx
import time

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

def extract_text_from_file(file):
    """파일에서 텍스트를 추출하는 함수"""
    try:
        guideline_text = ""
        filename = file.filename
        
        # 엑셀 파일 처리
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            app.logger.info(f"엑셀 파일 처리: {filename}")
            df = pd.read_excel(file, engine='openpyxl')
            guideline_text = ' '.join(df.astype(str).stack())
        
        # 워드 문서 처리
        elif filename.endswith('.docx'):
            app.logger.info(f"워드 문서 처리: {filename}")
            doc = docx.Document(file)
            guideline_text = "\n".join([para.text for para in doc.paragraphs])
        
        # 일반 텍스트 파일 처리
        else:
            app.logger.info(f"텍스트 파일 처리: {filename}")
            guideline_text = file.read().decode('utf-8', errors='ignore')
        
        return guideline_text, filename
    
    except Exception as e:
        app.logger.error(f"파일 '{filename}' 처리 중 오류: {e}")
        return None, filename

def call_gemini_with_retry(prompt, max_retries=3, initial_timeout=120):
    """재시도 로직과 타임아웃을 포함한 Gemini API 호출"""
    
    for attempt in range(max_retries):
        try:
            app.logger.info(f"Gemini API 호출 시도 {attempt + 1}/{max_retries}")
            
            # 모델 설정 - 타임아웃 증가
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # Generation Config 설정
            generation_config = {
                "temperature": 0.3,  # 일관성을 위해 낮은 온도
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 16384,  # 충분한 출력 토큰
            }
            
            # API 호출 (타임아웃 시간 증가)
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                request_options={"timeout": initial_timeout * (attempt + 1)}  # 재시도마다 타임아웃 증가
            )
            
            response_text = response.text
            app.logger.info("Gemini API 응답 수신 완료")
            return response_text
            
        except Exception as e:
            error_message = str(e)
            app.logger.warning(f"시도 {attempt + 1} 실패: {error_message}")
            
            # 마지막 시도가 아니면 재시도
            if attempt < max_retries - 1:
                wait_time = 5 * (attempt + 1)  # 지수 백오프
                app.logger.info(f"{wait_time}초 후 재시도...")
                time.sleep(wait_time)
            else:
                # 모든 재시도 실패
                app.logger.error(f"모든 재시도 실패: {error_message}")
                raise

# 자동 진단 API 엔드포인트 (다중 파일 지원)
@app.route("/api/diagnose", methods=["POST"])
def diagnose():
    # 파일이 요청에 포함되어 있는지 확인
    if 'guideline' not in request.files:
        app.logger.warning("파일이 업로드되지 않았습니다.")
        return jsonify({"error": "파일이 업로드되지 않았습니다."}), 400

    files = request.files.getlist('guideline')  # 여러 파일을 리스트로 받음

    if not files or all(f.filename == '' for f in files):
        app.logger.warning("빈 파일 이름이 제출되었습니다.")
        return jsonify({"error": "파일이 선택되지 않았습니다."}), 400
    
    try:
        # 모든 파일의 텍스트를 통합
        all_guideline_texts = []
        processed_files = []
        failed_files = []
        
        for file in files:
            if file.filename == '':
                continue
                
            guideline_text, filename = extract_text_from_file(file)
            
            if guideline_text and guideline_text.strip():
                all_guideline_texts.append(f"\n\n=== 파일명: {filename} ===\n{guideline_text}")
                processed_files.append(filename)
                app.logger.info(f"파일 '{filename}' 처리 완료, 내용 길이: {len(guideline_text)}")
            else:
                failed_files.append(filename)
                app.logger.warning(f"파일 '{filename}'에서 텍스트를 추출할 수 없습니다.")
        
        if not all_guideline_texts:
            app.logger.warning("모든 파일이 비어있거나 읽을 수 있는 텍스트가 없습니다.")
            return jsonify({
                "error": "업로드된 파일에서 읽을 수 있는 텍스트가 없습니다.",
                "failed_files": failed_files
            }), 400
        
        # 모든 파일의 텍스트를 하나로 통합
        combined_guideline_text = "\n".join(all_guideline_texts)
        
        # 텍스트가 너무 길면 자르기 (토큰 제한 고려)
        max_text_length = 200000  # 약 50,000 토큰
        if len(combined_guideline_text) > max_text_length:
            app.logger.warning(f"텍스트가 너무 깁니다 ({len(combined_guideline_text)}자). {max_text_length}자로 자릅니다.")
            combined_guideline_text = combined_guideline_text[:max_text_length] + "\n... (내용이 너무 길어 일부만 분석합니다)"
        
        app.logger.info(f"총 {len(processed_files)}개 파일 처리 완료: {', '.join(processed_files)}")
        if failed_files:
            app.logger.warning(f"처리 실패한 파일: {', '.join(failed_files)}")
        
        # Gemini API에 보낼 프롬프트 정의
        prompt = f"""
        당신은 ISMS-P 인증 심사 전문가입니다.
        아래에 제공되는 회사의 내부 지침서 내용을 분석하여, ISMS-P의 각 통제 항목을 만족하는지 진단해주세요.
        
        ★★★ 매우 중요한 지시사항 ★★★
        1. 반드시 101개 항목 전체에 대해 순서대로 응답하세요.
        2. 각 항목의 id, name, rating, reason, countermeasure는 반드시 해당 항목에만 해당하는 내용이어야 합니다.
        3. reason과 countermeasure 내용이 다른 항목과 섞이지 않도록 각 항목을 독립적으로 평가하세요.
        
        **평가 기준:**
        - 'Y'(양호): 지침서에 해당 항목에 대한 명확한 내용이 있음
        - 'P'(부분충족): 지침서에 일부 내용만 있거나 불완전함
        - 'N'(미흡): 지침서에 해당 항목에 대한 내용이 없거나 매우 부족함
        
        **reason 작성 규칙 (원인 분석):**
        - 반드시 해당 항목 ID와 name에 직접적으로 관련된 내용만 작성
        - 다른 항목의 내용을 절대 포함하지 말 것
        - Y 등급: 지침서에서 충족하는 구체적 내용을 50자 이내로 요약
        - P 등급: 불완전한 이유를 50-80자로 명확히 설명
        - N 등급: 부족한 이유를 50-80자로 구체적으로 설명
        
        **countermeasure 작성 규칙 (개선 방안):**
        - Y 등급: "현재 수준 유지 및 정기 점검" (15자 이내)
        - P 등급: 구체적이고 실행 가능한 조치 2-3가지 (100-150자)
        - N 등급: 명확하고 실행 가능한 조치 3-4가지 (150-200자)
        - 각 조치는 구체적이고 실무에서 즉시 적용 가능해야 함
        
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
            {{"id": "1.1.1", "name": "경영진의 참여", "rating": "Y/P/N", "reason": "평가 근거 및 원인", "countermeasure": "1) 조치사항 A 2) 조치사항 B"}},
            {{"id": "1.1.2", "name": "최고책임자의 지정", "rating": "Y/P/N", "reason": "평가 근거 및 원인", "countermeasure": "1) 조치사항 A 2) 조치사항 B"}},
            ...
            {{"id": "3.5.3", "name": "정보주체에 대한 통지", "rating": "Y/P/N", "reason": "평가 근거 및 원인", "countermeasure": "1) 조치사항 A 2) 조치사항 B"}}
          ]

          ---
          [회사 내부 지침서 내용]
          업로드된 파일 수: {len(processed_files)}개
          파일 목록: {', '.join(processed_files)}
          
          {combined_guideline_text}
          ---
        """
        
        # 재시도 로직을 포함한 API 호출
        response_text = call_gemini_with_retry(prompt, max_retries=3, initial_timeout=600)

        # 생성된 텍스트에서 JSON 부분만 추출
        # 마크다운 코드 블록(` ```json ... ``` `)을 제거
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        
        json_start = response_text.find('[')
        json_end = response_text.rfind(']') + 1
        
        if json_start == -1 or json_end == 0:
            app.logger.error("API 응답에서 유효한 JSON 배열을 찾지 못했습니다.")
            app.logger.debug(f"전체 응답 텍스트: {response_text[:1000]}...")
            return jsonify({"error": "진단 결과에서 유효한 형식을 찾지 못했습니다."}), 500
            
        json_response = response_text[json_start:json_end]
        
        # JSON 파싱 및 클라이언트에 전송
        diagnosis_data = json.loads(json_response)
        app.logger.info(f"JSON 파싱 성공, {len(diagnosis_data)}개 항목 포함")
        
        # 응답에 처리된 파일 정보 포함
        return jsonify({
            "data": diagnosis_data,
            "processed_files": processed_files,
            "failed_files": failed_files,
            "total_files": len(files)
        })

    except Exception as e:
        app.logger.error(f"진단 보고서 생성 중 오류 발생: {e}", exc_info=True)
        error_message = str(e)
        
        # 타임아웃 오류에 대한 구체적인 메시지
        if "Deadline Exceeded" in error_message or "timeout" in error_message.lower():
            return jsonify({
                "error": "분석 시간이 초과되었습니다. 문서 크기를 줄이거나 파일을 나누어 업로드해주세요.",
                "detail": "서버 처리 시간이 너무 오래 걸렸습니다."
            }), 504
        
        return jsonify({"error": "진단 보고서 생성 중 서버 오류가 발생했습니다."}), 500

# 서버 실행
if __name__ == "__main__":
    # 0.0.0.0으로 호스트를 설정하여 외부에서도 접속 가능하도록 함
    app.run(host='0.0.0.0', port=3001, debug=True)
