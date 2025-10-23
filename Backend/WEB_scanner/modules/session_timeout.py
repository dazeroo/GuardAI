# modules/session_timeout.py
# -*- coding: utf-8 -*-
"""
불충분한 세션 만료 진단
- 세션 쿠키의 만료 설정 및 로그아웃 처리 확인
"""

from typing import Dict, Any


def test_session_timeout(target: str, session) -> Dict[str, Any]:
    """
    세션 만료 정책 점검
    """
    try:
        cookies = session.cookies
        details = []
        weak_cookies = []

        for name, cookie in cookies.items():
            if cookie.expires is None:
                weak_cookies.append(name)
            if not cookie.secure:
                details.append(f"Cookie {name} missing 'Secure' flag")
            if 'httponly' not in cookie.__dict__.get('_rest', {}):
                details.append(f"Cookie {name} missing 'HttpOnly' flag")

        if weak_cookies:
            return {
                'status': '취약',
                'description': f'세션 쿠키 만료 설정이 없음 ({", ".join(weak_cookies)})',
                'details': details
            }

        if details:
            return {
                'status': '인터뷰',
                'description': '쿠키 보안 속성이 일부 누락됨',
                'details': details
            }

        return {
            'status': '양호',
            'description': '모든 세션 쿠키가 Secure/HttpOnly/만료 설정을 포함함',
            'details': []
        }

    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 오류 발생: {str(e)}',
            'details': []
        }
