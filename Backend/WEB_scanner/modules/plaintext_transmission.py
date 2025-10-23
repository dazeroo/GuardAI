#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modules/plaintext_transmission.py - 데이터 평문 전송 취약점 검사
"""

import re
from urllib.parse import urlparse


def test_plaintext_transmission(target_url, session):
    """데이터 평문 전송 취약점 검사"""
    
    vulnerabilities = []
    warnings = []
    
    try:
        parsed = urlparse(target_url)
        
        # 1. HTTP 사용 여부 확인
        if parsed.scheme == 'http':
            vulnerabilities.append("HTTP 프로토콜 사용 중 - 데이터가 평문으로 전송됩니다")
            
            # HTTPS 버전 확인
            https_url = target_url.replace('http://', 'https://')
            try:
                https_response = session.get(https_url, timeout=10)
                if https_response.status_code == 200:
                    warnings.append("HTTPS 사용 가능하나 강제되지 않음")
                else:
                    vulnerabilities.append("HTTPS가 지원되지 않거나 설정 오류")
            except:
                vulnerabilities.append("HTTPS가 지원되지 않음")
        
        # 2. HTTPS 사용 시 추가 검사
        if parsed.scheme == 'https':
            response = session.get(target_url, timeout=10)
            headers = response.headers
            
            # HSTS 헤더 확인
            if 'Strict-Transport-Security' not in headers:
                warnings.append("HSTS 헤더 미설정 - HTTP로 다운그레이드 가능")
            else:
                hsts_value = headers['Strict-Transport-Security']
                # max-age 확인
                if 'max-age' in hsts_value:
                    max_age_match = re.search(r'max-age=(\d+)', hsts_value)
                    if max_age_match:
                        max_age = int(max_age_match.group(1))
                        if max_age < 31536000:  # 1년 미만
                            warnings.append(f"HSTS max-age가 짧음: {max_age}초 (권장: 31536000)")
                
                # includeSubDomains 확인
                if 'includeSubDomains' not in hsts_value.lower():
                    warnings.append("HSTS에 includeSubDomains 미설정")
            
            # 3. Mixed Content 확인 (HTTPS 페이지에서 HTTP 리소스 로드)
            response_text = response.text
            http_resources = re.findall(r'(http://[^\s\'"<>]+)', response_text)
            
            if http_resources:
                unique_resources = list(set(http_resources))[:5]  # 최대 5개만
                warnings.append(f"Mixed Content 발견: HTTPS 페이지에서 {len(http_resources)}개의 HTTP 리소스 로드")
                for resource in unique_resources:
                    warnings.append(f"  - {resource}")
            
            # 4. 폼에서 HTTP로 데이터 전송 확인
            form_actions = re.findall(r'<form[^>]*action=["\']?(http://[^"\'\s>]+)["\']?', response_text, re.IGNORECASE)
            if form_actions:
                vulnerabilities.append("폼이 HTTP URL로 데이터를 전송합니다")
                for action in list(set(form_actions))[:3]:
                    vulnerabilities.append(f"  - {action}")
        
        # 5. 민감 정보 포함 여부 확인
        response = session.get(target_url, timeout=10)
        response_text = response.text.lower()
        
        sensitive_patterns = [
            (r'<input[^>]*type=["\']password["\']', '비밀번호 입력 필드'),
            (r'<input[^>]*name=["\']?(?:card|credit)', '신용카드 정보 입력'),
            (r'<input[^>]*name=["\']?(?:ssn|social)', '주민등록번호 입력'),
            (r'<input[^>]*name=["\']?(?:bank|account)', '계좌 정보 입력'),
        ]
        
        has_sensitive = False
        for pattern, desc in sensitive_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                has_sensitive = True
                if parsed.scheme == 'http':
                    vulnerabilities.append(f"{desc} 필드가 HTTP로 전송될 수 있음")
                break
        
        # 결과 평가
        if vulnerabilities:
            return {
                'status': '취약',
                'description': '데이터가 평문으로 전송되거나 보안 설정이 부족합니다',
                'details': vulnerabilities + warnings
            }
        elif warnings:
            return {
                'status': '인터뷰',
                'description': 'HTTPS를 사용하나 일부 보안 설정 개선이 필요합니다',
                'details': warnings
            }
        else:
            return {
                'status': '양호',
                'description': 'HTTPS를 사용하며 보안 설정이 적절합니다',
                'details': ['HTTPS 사용', 'HSTS 설정됨', 'Mixed Content 없음']
            }
    
    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 오류 발생: {str(e)}',
            'details': []
        }