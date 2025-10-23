#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modules/command_injection.py - 운영체제 명령 실행 취약점 검사
"""

import urllib.parse
from urllib.parse import urlparse, parse_qs
import time


def test_command_injection(target_url, session):
    """운영체제 명령 실행(Command Injection) 취약점 검사"""
    
    # 명령어 인젝션 페이로드
    payloads = [
        # Linux/Unix
        ('`whoami`', 'command substitution'),
        ('$(whoami)', 'command substitution'),
        ('; whoami', 'command chaining'),
        ('| whoami', 'pipe'),
        ('|| whoami', 'OR operator'),
        ('& whoami', 'background execution'),
        ('&& whoami', 'AND operator'),
        ('\n whoami', 'newline injection'),
        
        # Time-based (Blind)
        ('; sleep 5', 'time delay (Linux)'),
        ('& timeout 5', 'time delay (Windows)'),
        ('| sleep 5', 'pipe sleep'),
        
        # Windows
        ('& dir', 'Windows directory'),
        ('| dir', 'pipe dir'),
        ('&& dir', 'AND dir'),
    ]
    
    # 명령어 실행 결과 지표
    command_indicators = [
        'root', 'daemon', 'bin', 'sys',  # /etc/passwd 내용
        'www-data', 'apache', 'nginx',  # 웹서버 사용자
        'uid=', 'gid=',  # id 명령어 결과
        'Windows', 'System32', 'Program Files',  # Windows
        'Volume Serial Number',  # dir 명령어
    ]
    
    vulnerable = []
    
    try:
        parsed = urlparse(target_url)
        
        if not parsed.query:
            return {
                'status': '인터뷰',
                'description': 'URL에 파라미터가 없어 자동 검사가 불가능합니다',
                'details': ['GET 파라미터를 포함한 URL로 다시 테스트하세요']
            }
        
        params = parse_qs(parsed.query)
        
        # 기준 응답 시간 측정
        start_time = time.time()
        base_response = session.get(target_url, timeout=15)
        base_time = time.time() - start_time
        base_text = base_response.text
        
        # 각 파라미터에 대해 테스트
        for param_name in params:
            time_based_detected = False
            
            for payload, description in payloads:
                test_params = params.copy()
                test_params[param_name] = [payload]
                
                test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urllib.parse.urlencode(test_params, doseq=True)}"
                
                try:
                    # Time-based 테스트
                    if 'sleep' in payload or 'timeout' in payload:
                        start_time = time.time()
                        test_response = session.get(test_url, timeout=15)
                        response_time = time.time() - start_time
                        
                        # 5초 지연 페이로드의 경우
                        if 'sleep 5' in payload or 'timeout 5' in payload:
                            if response_time > base_time + 4:  # 최소 4초 지연
                                vulnerable.append(
                                    f"파라미터 '{param_name}'에서 Time-based Command Injection 감지 (지연: {response_time:.1f}초)"
                                )
                                time_based_detected = True
                                break
                    else:
                        # 출력 기반 테스트
                        test_response = session.get(test_url, timeout=15)
                        response_text = test_response.text
                        
                        # 명령어 실행 결과 확인
                        for indicator in command_indicators:
                            if indicator in response_text and indicator not in base_text:
                                vulnerable.append(
                                    f"파라미터 '{param_name}'에서 명령어 실행 가능 (지표: {indicator}, 페이로드: {payload})"
                                )
                                break
                        
                        # 에러 메시지로 명령어 실행 확인
                        error_patterns = [
                            'sh:', 'bash:', 'command not found',
                            'cannot execute', 'permission denied',
                            "'whoami'", '"whoami"',
                        ]
                        
                        for error in error_patterns:
                            if error.lower() in response_text.lower():
                                vulnerable.append(
                                    f"파라미터 '{param_name}'에서 명령어 실행 시도 감지 (에러: {error})"
                                )
                                break
                
                except Exception as e:
                    # 타임아웃은 정상 (sleep으로 인한 것일 수 있음)
                    if 'timeout' in str(e).lower() and ('sleep' in payload or 'timeout' in payload):
                        vulnerable.append(
                            f"파라미터 '{param_name}'에서 Time-based Command Injection 가능성 (타임아웃 발생)"
                        )
                        time_based_detected = True
                        break
                    continue
            
            if time_based_detected:
                break
        
        # 결과 반환
        if vulnerable:
            return {
                'status': '취약',
                'description': '운영체제 명령 실행 취약점이 발견되었습니다',
                'details': list(set(vulnerable))
            }
        else:
            return {
                'status': '양호',
                'description': '운영체제 명령 실행 취약점이 발견되지 않았습니다',
                'details': []
            }
    
    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 오류 발생: {str(e)}',
            'details': []
        }