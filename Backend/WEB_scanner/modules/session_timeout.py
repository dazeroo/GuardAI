# modules/session_timeout.py
# -*- coding: utf-8 -*-
"""
불충분한 세션 만료 진단
- 세션 쿠키의 보안 속성 및 서버 측 세션 만료 정책 확인
"""

import time
import requests
from typing import Dict, Any, List

# --- 기존 코드: 클라이언트 측 쿠키 보안 속성 검사 ---

def test_session_timeout_cookies_only(session) -> List[str]:
    """Secure, HttpOnly, 만료 설정 등 쿠키 보안 속성만 검사"""
    details = []
    
    for name, cookie in session.cookies.items():
        # 만료 설정 확인 (만료 시간이 없거나 너무 긴 경우는 수동 확인 필요)
        if cookie.expires is None:
            details.append(f"Cookie {name} missing explicit expiration setting (should be session cookie or have timeout)")
        
        # Secure 플래그 확인
        if not cookie.secure:
            details.append(f"Cookie {name} missing 'Secure' flag (Use HTTPS!)")
        
        # HttpOnly 플래그 확인
        # requests 라이브러리에서 httponly는 _rest 딕셔너리에 저장됨
        if 'httponly' not in cookie.__dict__.get('_rest', {}):
            details.append(f"Cookie {name} missing 'HttpOnly' flag (XSS risk)")
            
    return details


# --- 신규 코드: 서버 측 세션 만료 정책 검사 (CII 점검 방법 반영) ---

def test_server_side_session_timeout(login_url: str, post_data: Dict[str, str], 
                                     target_url: str, session, 
                                     session_timeout_seconds: int = 150) -> Dict[str, Any]:
    """
    CII 점검 방법 Step 1 반영: 로그인 후 일정 시간 경과 시 세션 유지 여부 확인
    
    주의: 이 테스트를 실행하려면 실제로 지정된 시간(session_timeout_seconds)만큼 지연됩니다.
    """
    
    # 1. 로그인하여 유효한 세션(쿠키) 획득
    try:
        # 새로운 세션 객체 생성 (기존 세션과 분리)
        test_session = requests.Session()
        login_response = test_session.post(login_url, data=post_data, timeout=10, allow_redirects=False)

        # 로그인 성공 여부 (상태 코드 및 리다이렉트 등으로 판단 필요. 여기서는 200/302로 가정)
        if login_response.status_code not in [200, 302]:
            return {
                'status': '인터뷰',
                'description': '로그인 실패: 세션 만료 테스트를 진행할 수 없음',
                'details': [f"로그인 URL {login_url}에서 200/302 응답 받지 못함"]
            }

        # 2. 로그인 직후 세션 유효성 확인 (기준 응답)
        initial_response = test_session.get(target_url, timeout=10)
        
        # 유효한 세션이 발급되었는지 확인 (로그인 전과 응답이 다른지 확인 필요)
        if 'Hello Admin' not in initial_response.text: # 예시 문구
            return {
                'status': '인터뷰',
                'description': '로그인 성공 후에도 유효한 세션 발급을 확인하지 못함',
                'details': []
            }
        
        details = [f"유효한 세션 획득 후 {target_url} 접근 성공 (200 OK)"]
        
        # 3. 세션 만료 시간 대기
        details.append(f"세션 만료 시간({session_timeout_seconds}초) 대기 중...")
        time.sleep(session_timeout_seconds) 
        
        # 4. 일정 시간 경과 후 세션 재사용 시도 (재인증 여부 확인)
        expired_response = test_session.get(target_url, timeout=10)
        
        # 5. 결과 판단
        
        # 로그인 페이지로 리다이렉트되거나(302), 권한 없음(401/403) 또는 로그아웃 메시지(200)가 나타나야 양호
        if 'login' in expired_response.text.lower() or expired_response.status_code in [401, 403, 302]:
            return {
                'status': '양호',
                'description': f'세션 만료 시간({session_timeout_seconds}초) 후 재인증이 요구됨',
                'details': [f"경과 후 응답 코드: {expired_response.status_code}. 만료 확인됨."]
            }
        else:
            # 세션이 여전히 유효하거나, 중요한 페이지에 접근 가능한 경우
            return {
                'status': '취약',
                'description': f'세션 만료 시간({session_timeout_seconds}초) 후에도 세션이 유지됨',
                'details': [f"경과 후에도 {target_url} 접근 가능 (200 OK)"]
            }

    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'세션 만료 검사 중 오류 발생: {str(e)}',
            'details': []
        }

# --- 메인 함수: 기존 test_session_timeout을 대체/확장 ---

def test_session_timeout(login_url: str, post_data: Dict[str, str], 
                          target_url_after_login: str, session) -> Dict[str, Any]:
    """
    세션 보안 전반을 검사하는 메인 함수
    """
    
    # 1. 쿠키 보안 속성 검사 (기존 로직)
    cookie_details = test_session_timeout_cookies_only(session)

    # 2. 서버 측 세션 만료 정책 검사 (CII 기준)
    # 실제 서버의 세션 타임아웃 시간에 맞춰 150초(2.5분)로 임의 설정
    server_timeout_result = test_server_side_session_timeout(
        login_url, post_data, target_url_after_login, session, session_timeout_seconds=150
    )

    # 3. 결과 통합
    if server_timeout_result['status'] == '취약':
        cookie_details.extend(server_timeout_result['details'])
        return {
            'status': '취약',
            'description': '불충분한 세션 만료 정책 (서버 측 타임아웃 실패)',
            'details': cookie_details
        }
    
    if cookie_details:
        # 쿠키 보안 속성 문제만 있는 경우
        return {
            'status': '인터뷰',
            'description': '쿠키 보안 속성이 일부 누락됨. 서버 만료는 통과.',
            'details': cookie_details
        }
    
    # 서버 만료도 통과하고 쿠키 보안도 양호한 경우
    return {
        'status': '양호',
        'description': '세션 만료 정책 및 쿠키 보안 속성 양호',
        'details': server_timeout_result['details']
    }
