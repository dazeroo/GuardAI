#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modules/session_fixation.py - 세션 고정 취약점 검사
"""

import re
from urllib.parse import urlparse, parse_qs


def test_session_fixation(target_url, session):
    """세션 고정 취약점 검사"""
    
    vulnerabilities = []
    warnings = []
    
    try:
        parsed = urlparse(target_url)
        
        # 1. URL에 세션 ID 노출 확인
        query_params = parse_qs(parsed.query)
        
        session_param_names = [
            'sessionid', 'session_id', 'session', 'sid', 'ssid',
            'phpsessid', 'jsessionid', 'aspsessionid', 'asp.net_sessionid'
        ]
        
        for param_name in query_params:
            if any(session_name in param_name.lower() for session_name in session_param_names):
                vulnerabilities.append(f"URL에 세션 ID 노출: 파라미터 '{param_name}'")
                vulnerabilities.append("  세션 ID가 URL에 포함되면 세션 고정 공격에 취약합니다")
        
        # 2. 첫 번째 요청에서 세션 쿠키 받기
        response1 = session.get(target_url, timeout=10)
        cookies1 = {cookie.name: cookie.value for cookie in response1.cookies}
        
        # 세션 관련 쿠키 찾기
        session_cookies = {}
        for cookie_name, cookie_value in cookies1.items():
            if any(name in cookie_name.lower() for name in session_param_names):
                session_cookies[cookie_name] = cookie_value
        
        if not session_cookies:
            return {
                'status': '인터뷰',
                'description': '세션 쿠키가 발견되지 않아 검사할 수 없습니다',
                'details': ['로그인 페이지나 세션을 사용하는 페이지에서 테스트하세요']
            }
        
        # 3. 동일 URL에 두 번째 요청
        response2 = session.get(target_url, timeout=10)
        cookies2 = {cookie.name: cookie.value for cookie in response2.cookies}
        
        # 세션 ID 비교
        for cookie_name in session_cookies:
            if cookie_name in cookies2:
                if session_cookies[cookie_name] == cookies2[cookie_name]:
                    warnings.append(f"세션 쿠키 '{cookie_name}'가 재사용됨 (동일한 값 유지)")
                else:
                    warnings.append(f"세션 쿠키 '{cookie_name}'가 요청마다 변경됨 (정상)")
        
        # 4. HTML에서 세션 ID 노출 확인
        response_text = response1.text
        
        # JavaScript에서 세션 ID 노출
        js_session_patterns = [
            r'sessionId\s*[:=]\s*["\']([^"\']+)["\']',
            r'session_id\s*[:=]\s*["\']([^"\']+)["\']',
            r'var\s+session\s*=\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in js_session_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            if matches:
                vulnerabilities.append("JavaScript에서 세션 ID 노출 가능")
                break
        
        # 5. Hidden 필드에 세션 ID
        hidden_session = re.findall(
            r'<input[^>]*type=["\']hidden["\'][^>]*name=["\']([^"\']*session[^"\']*)["\']',
            response_text,
            re.IGNORECASE
        )
        
        if hidden_session:
            warnings.append(f"Hidden 필드에 세션 관련 값: {', '.join(hidden_session)}")
        
        # 6. 로그인 폼 확인
        has_login_form = bool(re.search(
            r'<form[^>]*>.*?<input[^>]*type=["\']password["\']',
            response_text,
            re.DOTALL | re.IGNORECASE
        ))
        
        if has_login_form and session_cookies:
            warnings.append("로그인 폼이 존재합니다 - 로그인 전후 세션 ID 변경 여부 확인 필요")
            warnings.append("  (수동 테스트: 로그인 전 세션 ID를 저장하고 로그인 후 변경되는지 확인)")
        
        # 7. 세션 쿠키 속성 확인
        for cookie in response1.cookies:
            if any(name in cookie.name.lower() for name in session_param_names):
                issues = []
                
                if not cookie.secure:
                    issues.append("Secure 속성 없음")
                
                if not cookie.has_nonstandard_attr('HttpOnly'):
                    issues.append("HttpOnly 속성 없음")
                
                # SameSite 확인
                samesite = None
                if cookie.has_nonstandard_attr('SameSite'):
                    samesite = cookie.get_nonstandard_attr('SameSite')
                
                if not samesite:
                    issues.append("SameSite 속성 없음 - CSRF 취약")
                
                if issues:
                    warnings.append(f"세션 쿠키 '{cookie.name}' 보안 속성 부족: {', '.join(issues)}")
        
        # 8. Referer 헤더에서 세션 ID 유출 가능성
        links = re.findall(r'href=["\']([^"\']+)["\']', response_text)
        external_links = [link for link in links if link.startswith('http') and parsed.netloc not in link]
        
        if external_links and any('session' in parsed.query.lower() for parsed in [urlparse(target_url)]):
            warnings.append("외부 링크가 있고 URL에 세션 ID가 있어 Referer 헤더로 유출 가능")
        
        # 결과 평가
        if vulnerabilities:
            return {
                'status': '취약',
                'description': '세션 고정 취약점이 발견되었습니다',
                'details': vulnerabilities + warnings
            }
        elif warnings:
            return {
                'status': '인터뷰',
                'description': '세션 관리에 일부 취약점이 있을 수 있습니다. 추가 확인이 필요합니다',
                'details': warnings
            }
        else:
            return {
                'status': '양호',
                'description': '세션 고정 취약점이 발견되지 않았습니다',
                'details': ['세션 쿠키 사용', '보안 속성 적절', 'URL에 세션 ID 없음']
            }
    
    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 오류 발생: {str(e)}',
            'details': []
        }