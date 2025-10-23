#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# modules/sql_injection.py - SQL 인젝션 취약점 검사


import urllib.parse
from urllib.parse import urlparse, parse_qs


def test_sql_injection(target_url, session):
    """SQL 인젝션 취약점 검사"""
    
    # SQL 인젝션 페이로드
    payloads = [
        "' OR '1'='1",
        "\" OR \"1\"=\"1",
        "' OR '1'='1' --",
        "' OR '1'='1' /*",
        "admin' --",
        "admin' #",
        "admin'/*",
        "' OR 1=1--",
        "' OR 1=1#",
        "' OR 1=1/*",
        "1' UNION SELECT NULL--",
        "1' UNION SELECT NULL,NULL--",
        "' AND 1=1--",
        "' AND 1=0--",
        "1' AND '1'='1",
        "1' AND '1'='2",
    ]
    
    # SQL 에러 메시지 패턴
    sql_errors = [
        "SQL syntax",
        "mysql_fetch",
        "mysql_num_rows",
        "mysqli",
        "ORA-",
        "PostgreSQL",
        "Microsoft SQL",
        "ODBC",
        "SQLite",
        "Unclosed quotation",
        "syntax error",
        "Invalid query",
        "mysql_query",
        "pg_query",
        "sqlite_query",
        "Warning: mysql",
        "supplied argument is not a valid MySQL",
        "Division by zero in",
        "Microsoft OLE DB Provider",
        "SQLSTATE",
    ]
    
    vulnerable = []
    
    try:
        # 기본 요청으로 정상 응답 확인
        base_response = session.get(target_url, timeout=10)
        base_length = len(base_response.text)
        
        parsed = urlparse(target_url)
        
        # URL에 파라미터가 없으면 검사 불가
        if not parsed.query:
            return {
                'status': '인터뷰',
                'description': 'URL에 파라미터가 없어 자동 검사가 불가능합니다. 수동 확인이 필요합니다.',
                'details': ['GET 파라미터를 포함한 URL로 다시 테스트하세요']
            }
        
        params = parse_qs(parsed.query)
        
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
                    response_text = test_response.text.lower()
                    
                    # SQL 에러 메시지 확인
                    for error in sql_errors:
                        if error.lower() in response_text:
                            vulnerable.append(f"파라미터 '{param_name}'에서 SQL 에러 감지: {error}")
                            break
                    
                    # 응답 길이 차이로 Boolean-based SQL Injection 감지
                    length_diff = abs(len(test_response.text) - base_length)
                    if length_diff > 100:  # 100자 이상 차이나면 의심
                        if "' AND 1=1" in payload or "' AND 1=0" in payload:
                            vulnerable.append(f"파라미터 '{param_name}'에서 Boolean-based SQL Injection 의심 (응답 길이 차이: {length_diff})")
                
                except Exception:
                    continue
        
        # 결과 반환
        if vulnerable:
            # 중복 제거
            vulnerable = list(set(vulnerable))
            return {
                'status': '취약',
                'description': 'SQL 인젝션 취약점이 발견되었습니다',
                'details': vulnerable
            }
        else:
            return {
                'status': '양호',
                'description': 'SQL 인젝션 취약점이 발견되지 않았습니다',
                'details': []
            }
    
    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 오류 발생: {str(e)}',
            'details': []
        }
