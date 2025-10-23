#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modules/insufficient_authentication.py - 불충분한 인증 취약점 검사
"""

import re
from urllib.parse import urlparse, urljoin
import base64


def test_insufficient_authentication(target_url, session):
    """불충분한 인증 취약점 검사"""
    
    vulnerabilities = []
    warnings = []
    
    try:
        parsed = urlparse(target_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # 1. 기본 요청
        response = session.get(target_url, timeout=10)
        response_text = response.text
        
        # 2. HTTP Basic Authentication 확인
        if response.status_code == 401:
            auth_header = response.headers.get('WWW-Authenticate', '')
            
            if 'Basic' in auth_header:
                warnings.append("HTTP Basic Authentication 사용 중")
                
                # HTTPS 여부 확인
                if parsed.scheme == 'http':
                    vulnerabilities.append("HTTP Basic Auth를 평문 HTTP로 사용 (자격증명 노출 위험)")
                
                # 기본 자격증명 테스트
                default_creds = [
                    ('admin', 'admin'),
                    ('admin', 'password'),
                    ('admin', ''),
                    ('root', 'root'),
                    ('test', 'test'),
                    ('guest', 'guest'),
                ]
                
                for username, password in default_creds:
                    try:
                        auth_str = f"{username}:{password}"
                        encoded = base64.b64encode(auth_str.encode()).decode()
                        
                        test_response = session.get(
                            target_url,
                            headers={'Authorization': f'Basic {encoded}'},
                            timeout=10
                        )
                        
                        if test_response.status_code == 200:
                            vulnerabilities.append(
                                f"기본 자격증명으로 인증 성공: {username}/{password}"
                            )
                            break
                    except:
                        pass
        
        # 3. 로그인 폼 확인
        login_patterns = [
            r'<form[^>]*>.*?<input[^>]*type=["\']password["\'].*?</form>',
            r'<input[^>]*type=["\']password["\']',
        ]
        
        has_login_form = False
        for pattern in login_patterns:
            if re.search(pattern, response_text, re.DOTALL | re.IGNORECASE):
                has_login_form = True
                break
        
        if has_login_form:
            # 4. CAPTCHA 존재 여부
            captcha_indicators = [
                'captcha', 'recaptcha', 'g-recaptcha',
                'hcaptcha', 'turnstile'
            ]
            
            has_captcha = any(indicator in response_text.lower() for indicator in captcha_indicators)
            
            if not has_captcha:
                warnings.append("로그인 폼에 CAPTCHA가 없음 - 브루트포스 공격 취약")
            
            # 5. 계정 잠금 메커니즘 확인 (텍스트 기반)
            lockout_indicators = [
                'account locked', 'too many attempts',
                'temporarily disabled', 'locked out',
                '계정 잠금', '잠금 해제', '시도 횟수'
            ]
            
            has_lockout_hint = any(indicator in response_text.lower() for indicator in lockout_indicators)
            
            if not has_lockout_hint:
                warnings.append("계정 잠금 메커니즘 확인 불가 - 수동 확인 필요")
            
            # 6. 비밀번호 입력 필드 autocomplete 확인
            password_fields = re.findall(
                r'<input[^>]*type=["\']password["\'][^>]*>',
                response_text,
                re.IGNORECASE
            )
            
            for field in password_fields:
                if 'autocomplete' not in field.lower() or 'autocomplete="on"' in field.lower():
                    warnings.append("비밀번호 필드에 autocomplete 미설정 또는 활성화")
                    break
            
            # 7. Remember Me 기능
            remember_patterns = [
                r'<input[^>]*name=["\']remember',
                r'<label[^>]*>.*?remember.*?me',
                r'<input[^>]*value=["\']remember',
            ]
            
            for pattern in remember_patterns:
                if re.search(pattern, response_text, re.IGNORECASE):
                    warnings.append("'Remember Me' 기능 존재 - 구현 보안 확인 필요")
                    break
        
        # 8. 관리자 페이지 직접 접근 시도
        admin_paths = [
            '/admin', '/admin/', '/administrator',
            '/admin/dashboard', '/admin/index.php',
            '/wp-admin/', '/manage',
        ]
        
        for admin_path in admin_paths:
            try:
                admin_url = urljoin(base_url, admin_path)
                admin_response = session.get(admin_url, timeout=10, allow_redirects=False)
                
                # 인증 없이 200 응답
                if admin_response.status_code == 200:
                    if 'login' not in admin_response.text.lower():
                        vulnerabilities.append(
                            f"관리자 페이지 인증 없이 접근 가능: {admin_path}"
                        )
                
                # 301/302는 정상 (로그인으로 리다이렉트)
                # 403도 정상 (접근 거부)
            except:
                pass
        
        # 9. API 엔드포인트 인증 확인
        api_paths = [
            '/api', '/api/', '/api/v1',
            '/rest', '/rest/api',
            '/graphql',
        ]
        
        for api_path in api_paths:
            try:
                api_url = urljoin(base_url, api_path)
                api_response = session.get(api_url, timeout=10)
                
                if api_response.status_code == 200:
                    # JSON 응답이면서 에러가 아닌 경우
                    if 'application/json' in api_response.headers.get('Content-Type', ''):
                        if 'error' not in api_response.text.lower() and 'unauthorized' not in api_response.text.lower():
                            warnings.append(f"API 엔드포인트 인증 확인 필요: {api_path}")
            except:
                pass
        
        # 10. 세션/토큰 없이 접근 가능한 기능
        if response.status_code == 200:
            # 민감한 기능이 있는지 확인
            sensitive_patterns = [
                (r'<form[^>]*action=[^>]*delete', '삭제 기능'),
                (r'<form[^>]*action=[^>]*update', '수정 기능'),
                (r'<a[^>]*href=[^>]*delete', '삭제 링크'),
                (r'<button[^>]*>.*?delete.*?</button>', '삭제 버튼'),
            ]
            
            for pattern, desc in sensitive_patterns:
                if re.search(pattern, response_text, re.IGNORECASE):
                    warnings.append(f"{desc}이 인증 없이 노출됨 - 실제 실행 가능 여부 확인 필요")
        
        # 결과 평가
        if vulnerabilities:
            return {
                'status': '취약',
                'description': '불충분한 인증 취약점이 발견되었습니다',
                'details': vulnerabilities + warnings
            }
        elif warnings:
            return {
                'status': '인터뷰',
                'description': '인증 메커니즘에 일부 개선이 필요할 수 있습니다',
                'details': warnings
            }
        else:
            return {
                'status': '양호',
                'description': '인증이 적절히 구현되어 있습니다',
                'details': []
            }
    
    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 오류 발생: {str(e)}',
            'details': []
        }