# modules/weak_password.py
# -*- coding: utf-8 -*-
"""
약한 문자열(비밀번호) 강도 정책 진단
- 회원가입/비밀번호 변경 페이지의 비밀번호 정책 점검
"""
import re
import requests
from typing import Dict, Any

def test_weak_string(login_url: str, session, username_param: str, password_param: str) -> Dict[str, Any]:
    """
    일정 횟수 이상 인증 실패 시 로그인을 제한하는지 확인
    """
    
    # 1. 테스트 설정
    MAX_ATTEMPTS = 5         # 테스트 시도 횟수
    TEST_USERNAME = "non_exist_user_12345"
    TEST_PASSWORD = "wrong_password_12345"
    
    # 로그인 제한 탐지 키워드 (서버 응답에서 찾을 패턴)
    limit_indicators = [
        'locked', '차단', '잠금', '계정이 정지', '횟수 초과', '5 minutes',
        'brute-force', '로그인 시도 제한'
    ]
    
    # 2. 반복 로그인 시도
    detected = False
    details = []
    
    try:
        for attempt in range(1, MAX_ATTEMPTS + 2): # 최대 시도 횟수보다 1번 더 시도
            payload = {
                username_param: TEST_USERNAME,
                password_param: TEST_PASSWORD
            }
            response = session.post(login_url, data=payload, timeout=5)
            response_text = response.text.lower()
            
            # 응답에서 제한 지표 확인
            if any(word in response_text for word in limit_indicators):
                detected = True
                details.append(f"로그인 시도 {attempt}회 후 제한 메시지 발견: {response_text[:50]}...")
                break
                
    except requests.exceptions.Timeout:
        details.append("로그인 요청 중 타임아웃 발생")
    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 예외 발생: {str(e)}',
            'details': []
        }

    # 3. 결과 반환
    if detected:
        return {
            'status': '양호',
            'description': f'로그인 실패 횟수 제한 정책이 발견되었습니다 ({attempt}회 후 제한)',
            'details': details
        }
    else:
        return {
            'status': '취약',
            'description': '반복적인 인증 실패에도 로그인 제한 정책이 확인되지 않음',
            'details': [f'{MAX_ATTEMPTS + 1}회 이상의 잘못된 로그인 시도 후에도 제한 메시지가 발견되지 않음']
        }
