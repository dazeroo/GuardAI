# modules/process_validation_omission.py
# -*- coding: utf-8 -*-
"""
21. 프로세스 검증 누락 (인가 우회) 취약점 검사
- 인증이 필요한 페이지에 유효한 세션 검증 로직이 누락되었는지 확인
"""
import requests
from typing import Dict, Any

def test_process_info_leak(
    login_url: str, 
    post_data: Dict[str, str], 
    protected_url: str, 
    session, 
    non_protected_url: str = None
) -> Dict[str, Any]:
    """
    프로세스 검증 누락(인가 우회) 취약점 검사.
    
    CII 점검 방법 (Step 3) 반영: 
    1. 로그인하여 유효한 세션을 획득한다.
    2. 유효한 세션 없이 중요 페이지에 직접 접근을 시도하여 인증이 누락되었는지 확인한다.
    """
    
    issues = []
    
    # 필수 매개변수 누락 시 인터뷰 반환
    if not login_url or not post_data or not protected_url:
        return {
            'status': '인터뷰',
            'description': '프로세스 검증 누락 테스트를 위한 로그인 정보(URL, Data) 및 중요 페이지 URL이 필요합니다',
            'details': []
        }

    # 1. 유효한 세션으로 중요 페이지에 접근하는 기준 응답 획득 (Baseline)
    try:
        logged_in_session = requests.Session()
        login_response = logged_in_session.post(login_url, data=post_data, timeout=10)
        
        # 로그인 실패 시 검사 불가
        if 'login failed' in login_response.text.lower() or login_response.status_code != 200: 
             return {
                'status': '인터뷰',
                'description': '로그인 실패로 프로세스 검증 누락 테스트 진행 불가',
                'details': [f"로그인 URL 응답 코드: {login_response.status_code}"]
            }
        
        baseline_response = logged_in_session.get(protected_url, timeout=10)
        baseline_status = baseline_response.status_code
        
        if baseline_status not in [200, 302]: # 세션이 있어도 중요 페이지 접근 불가 시
             return {
                'status': '인터뷰',
                'description': '유효한 세션으로 중요 페이지 접근 불가. 테스트 설정 확인 필요',
                'details': [f"중요 페이지 기준 응답 코드: {baseline_status}"]
            }
            
    except Exception as e:
        return {'status':'인터뷰', 'description':f'기준 요청 실패: {e}', 'details':[]}
        
    # 2. 비인증(Anon) 상태로 중요 페이지에 직접 접근 시도
    # 새롭고 깨끗한 세션(로그인하지 않은 상태) 사용
    try:
        anonymous_session = requests.Session()
        unauth_response = anonymous_session.get(protected_url, timeout=10, allow_redirects=False)
        unauth_status = unauth_response.status_code
        
        # 3. 판단 기준 적용: 인증 없이 직접 접근 시 성공하면 취약
        # '취약: 인증이 필요한 페이지를 로그인하지 않고 직접 접근할 때 접근이 가능한 경우'
        if unauth_status == 200:
            # 200 OK이면서, 내용이 로그인 페이지가 아닌 경우 (내용 비교는 복잡하므로 간단화)
            if 'login' not in unauth_response.text.lower(): 
                 issues.append(f"비인증 상태로 중요 페이지({protected_url})에 직접 접근 성공 (200 OK)")
            
        # 4. 양호/취약 결과 반환
        if issues:
            return {
                'status':'취약',
                'description':'프로세스 검증 누락(인가 우회) 취약점 발견',
                'details': issues
            }
        
        # 401(인증 필요), 403(접근 거부), 302/301(로그인 페이지 리다이렉트)는 양호
        if unauth_status in [401, 403, 301, 302]:
            return {
                'status':'양호',
                'description':'인증이 필요한 페이지에 대한 접근통제(인가) 로직이 구현됨',
                'details': [f"비인증 접근 시 응답 코드: {unauth_status}. 접근 차단 확인됨."]
            }
            
        # 기타 응답 코드 (5xx, 404 등)는 재확인 필요
        return {
            'status':'인터뷰',
            'description':'비인증 접근 시 예상치 못한 응답 코드 반환',
            'details': [f"비인증 접근 시 응답 코드: {unauth_status}. 수동 분석 필요."]
        }
            
    except Exception as e:
        return {'status':'인터뷰', 'description':f'비인증 접근 요청 실패: {e}', 'details':[]}
