#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modules/directory_indexing.py - 디렉터리 인덱싱 취약점 검사
"""

from urllib.parse import urlparse, urljoin


def test_directory_indexing(target_url, session):
    """디렉터리 인덱싱 취약점 검사"""
    
    # 테스트할 일반적인 디렉터리 경로
    test_paths = [
        '/',
        '/admin/',
        '/backup/',
        '/backups/',
        '/config/',
        '/uploads/',
        '/upload/',
        '/images/',
        '/img/',
        '/files/',
        '/file/',
        '/temp/',
        '/tmp/',
        '/log/',
        '/logs/',
        '/data/',
        '/downloads/',
        '/docs/',
        '/assets/',
        '/media/',
        '/static/',
        '/public/',
        '/private/',
        '/test/',
        '/old/',
        '/new/',
        '/archive/',
    ]
    
    # 디렉터리 인덱싱 탐지 패턴
    indexing_indicators = [
        'Index of',
        'Directory listing',
        'Parent Directory',
        '[DIR]',
        '<title>Index of',
        'Name</th>',
        'Size</th>',
        'Last modified</th>',
        '<h1>Index of',
        'Directory Listing For',
        '[To Parent Directory]',
    ]
    
    vulnerable = []
    
    try:
        parsed = urlparse(target_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        for path in test_paths:
            try:
                test_url = urljoin(base_url, path)
                response = session.get(test_url, timeout=10)
                
                # 200 OK 응답인 경우에만 확인
                if response.status_code == 200:
                    response_text = response.text
                    
                    # 디렉터리 인덱싱 지표 확인
                    for indicator in indexing_indicators:
                        if indicator in response_text:
                            vulnerable.append(f"디렉터리 인덱싱 활성화: {path}")
                            break
            
            except Exception:
                continue
        
        # 결과 반환
        if vulnerable:
            return {
                'status': '취약',
                'description': '디렉터리 인덱싱이 활성화되어 있어 파일 목록이 노출됩니다',
                'details': list(set(vulnerable))
            }
        else:
            return {
                'status': '양호',
                'description': '디렉터리 인덱싱이 비활성화되어 있습니다',
                'details': []
            }
    
    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 오류 발생: {str(e)}',
            'details': []
        }