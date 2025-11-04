#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modules/cookie_manipulation.py - 쿠키 변조 취약점 검사
"""

import base64
import json
import re


def test_cookie_manipulation(target_url, session):
    """쿠키 변조 취약점 검사"""
    
    vulnerabilities = []
    warnings = []
    
    try:
        response = session.get(target_url, timeout=10)
        cookies = response.cookies
        
        if not cookies:
            return {
                'status': '양호',
                'description': '쿠키가 설정되지 않았습니다',
                'details': []
            }
        
        for cookie in cookies:
            cookie_name = cookie.name
            cookie_value = cookie.value
            
            # 1. 쿠키 값이 암호화/서명되지 않은 경우
            
            # Base64 디코딩 시도
            try:
                decoded = base64.b64decode(cookie_value + '==')  # 패딩 추가
                decoded_str = decoded.decode('utf-8', errors='ignore')
                
                # JSON 형태인지 확인
                if decoded_str.startswith('{') or decoded_str.startswith('['):
                    try:
                        json_data = json.loads(decoded_str)
                        vulnerabilities.append(
                            f"쿠키 '{cookie_name}': Base64로 인코딩된 JSON (암호화/서명 없음)"
                        )
                        vulnerabilities.append(f"  디코딩된 내용: {str(json_data)[:100]}")
                    except:
                        pass
                
                # 읽을 수 있는 텍스트인지 확인
                if any(keyword in decoded_str.lower() for keyword in ['user', 'admin', 'role', 'id', 'email']):
                    vulnerabilities.append(
                        f"쿠키 '{cookie_name}': Base64 인코딩만으로 민감 정보 보호 (변조 가능)"
                    )
            except:
                pass
            
            # 2. 평문 정보 확인
            plaintext_patterns = [
                (r'user[:=](\w+)', '사용자 정보'),
                (r'role[:=](\w+)', '권한 정보'),
                (r'admin[:=](\w+)', '관리자 여부'),
                (r'id[:=](\d+)', 'ID 정보'),
                (r'email[:=]([\w@.]+)', '이메일'),
            ]
            
            for pattern, desc in plaintext_patterns:
                match = re.search(pattern, cookie_value, re.IGNORECASE)
                if match:
                    vulnerabilities.append(
                        f"쿠키 '{cookie_name}': {desc}가 평문으로 저장됨 ({match.group(1)})"
                    )
            
            # 3. 예측 가능한 쿠키 값
            if cookie_value.isdigit():
                vulnerabilities.append(
                    f"쿠키 '{cookie_name}': 순차적인 숫자 값 ({cookie_value}) - 예측 가능"
                )
            
            # 4. 단순한 값 (true/false, 0/1)
            if cookie_value.lower() in ['true', 'false', '0', '1', 'yes', 'no']:
                vulnerabilities.append(
                    f"쿠키 '{cookie_name}': 단순한 boolean 값 ({cookie_value}) - 쉽게 변조 가능"
                )
            
            # 5. 서명 확인
            # JWT 형식 확인
            if cookie_value.count('.') == 2:
                parts = cookie_value.split('.')
                try:
                    # JWT 헤더 디코딩
                    header = json.loads(base64.b64decode(parts[0] + '==').decode())
                    
                    # alg: none 취약점
                    if header.get('alg', '').lower() == 'none':
                        vulnerabilities.append(
                            f"쿠키 '{cookie_name}': JWT의 알고리즘이 'none' (서명 없음)"
                        )
                    
                    # 약한 알고리즘
                    weak_algs = ['HS256', 'RS256']  # 키 관리가 중요
                    if header.get('alg') in weak_algs:
                        warnings.append(
                            f"쿠키 '{cookie_name}': JWT 알고리즘 {header.get('alg')} 사용 - 키 관리 확인 필요"
                        )
                    
                    # 페이로드 디코딩
                    payload = json.loads(base64.b64decode(parts[1] + '==').decode())
                    
                    # 만료 시간 확인
                    if 'exp' not in payload:
                        warnings.append(
                            f"쿠키 '{cookie_name}': JWT에 만료 시간(exp) 없음"
                        )
                    
                    warnings.append(f"쿠키 '{cookie_name}': JWT 형식 사용 중")
                except:
                    pass
            
            # 6. 쿠키 길이가 너무 짧은 경우 (해시가 아닌 경우)
            if len(cookie_value) < 16 and not cookie_value.isalnum():
                warnings.append(
                    f"쿠키 '{cookie_name}': 값이 짧음 ({len(cookie_value)}자) - 예측 가능성 확인 필요"
                )
            
            # 7. 일반적인 세션 ID 패턴이 아닌 경우
            if not re.match(r'^[a-f0-9]{32,}$', cookie_value, re.IGNORECASE):
                # 32자 이상의 hex 문자열이 아니면
                if 'session' in cookie_name.lower():
                    warnings.append(
                        f"쿠키 '{cookie_name}': 표준 세션 ID 형식이 아님 - 보안 강도 확인 필요"
                    )
        
        # 8. 민감한 쿠키 이름 확인
        sensitive_names = ['user', 'username', 'userid', 'role', 'admin', 'privilege', 'auth']
        for cookie in cookies:
            if any(name in cookie.name.lower() for name in sensitive_names):
                # 보안 속성 확인
                if not cookie.secure:
                    vulnerabilities.append(
                        f"민감한 쿠키 '{cookie.name}'에 Secure 속성 없음 - HTTP로 전송 가능"
                    )
                if not cookie.has_nonstandard_attr('HttpOnly'):
                    vulnerabilities.append(
                        f"민감한 쿠키 '{cookie.name}'에 HttpOnly 속성 없음 - JavaScript로 접근 가능"
                    )
        
        # 결과 평가
        if vulnerabilities:
            return {
                'status': '취약',
                'description': f'쿠키 변조 취약점이 발견되었습니다 ({len(vulnerabilities)}개)',
                'details': vulnerabilities + warnings
            }
        elif warnings:
            return {
                'status': '인터뷰',
                'description': '쿠키 구현에 일부 개선이 필요할 수 있습니다',
                'details': warnings
            }
        else:
            return {
                'status': '양호',
                'description': '쿠키가 적절히 보호되고 있습니다',
                'details': ['쿠키 암호화/서명 사용', '보안 속성 적절']
            }
    
    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 오류 발생: {str(e)}',
            'details': []
        }