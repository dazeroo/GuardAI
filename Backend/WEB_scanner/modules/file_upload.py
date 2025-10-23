#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modules/file_upload.py - 파일 업로드 취약점 검사
"""

import re


def test_file_upload(target_url, session):
    """파일 업로드 취약점 검사"""
    
    try:
        response = session.get(target_url, timeout=10)
        response_text = response.text
        
        # 파일 업로드 폼 탐지 패턴
        upload_patterns = [
            r'<input[^>]*type=["\']file["\'][^>]*>',
            r'enctype=["\']multipart/form-data["\']',
            r'accept=["\'][^"\']*\.(jpg|png|pdf|doc|zip)[^"\']*["\']',
        ]
        
        has_upload = False
        for pattern in upload_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                has_upload = True
                break
        
        if not has_upload:
            return {
                'status': '양호',
                'description': '파일 업로드 기능이 발견되지 않았습니다',
                'details': []
            }
        
        # 위험한 파일 확장자 목록
        dangerous_exts = [
            'php', 'php3', 'php4', 'php5', 'phtml',
            'jsp', 'jspx',
            'asp', 'aspx', 'cer', 'asa',
            'exe', 'com', 'bat', 'cmd',
            'sh', 'bash',
            'py', 'rb', 'pl',
            'jar', 'war',
            'htaccess', 'config'
        ]
        
        vulnerabilities = []
        warnings = []
        
        # 파일 업로드 input 필드 찾기
        file_inputs = re.findall(r'<input[^>]*type=["\']file["\'][^>]*>', response_text, re.IGNORECASE)
        
        for file_input in file_inputs:
            # accept 속성 확인
            accept_match = re.search(r'accept=["\']([^"\']*)["\']', file_input, re.IGNORECASE)
            
            if accept_match:
                accept_value = accept_match.group(1).lower()
                
                # 위험한 확장자가 허용되는지 확인
                for ext in dangerous_exts:
                    if ext in accept_value or '*' in accept_value:
                        vulnerabilities.append(
                            f"위험한 파일 확장자 허용 가능: .{ext}"
                        )
                        break
                
                warnings.append(f"클라이언트 측 검증 발견: accept='{accept_value}'")
            else:
                vulnerabilities.append("accept 속성 미설정 - 모든 파일 형식 업로드 가능")
        
        # JavaScript 검증 확인
        js_validation_patterns = [
            r'\.split\(["\']\.["\']\)',
            r'extension',
            r'file\.name',
            r'allowedExtensions',
            r'fileType',
        ]
        
        has_js_validation = False
        for pattern in js_validation_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                has_js_validation = True
                warnings.append("JavaScript 파일 검증 발견 (우회 가능)")
                break
        
        # 최대 파일 크기 제한 확인
        if 'maxlength' not in response_text.lower() and 'max-size' not in response_text.lower():
            warnings.append("파일 크기 제한 미발견")
        
        # 결과 평가
        if vulnerabilities:
            return {
                'status': '취약',
                'description': '파일 업로드 시 보안 검증이 부족합니다',
                'details': vulnerabilities + warnings
            }
        elif warnings:
            return {
                'status': '인터뷰',
                'description': '파일 업로드 기능이 존재하며 서버 측 검증 확인이 필요합니다',
                'details': warnings + ['서버 측 확장자/MIME 타입 검증 수동 확인 필요', '업로드된 파일 실행 권한 확인 필요']
            }
        else:
            return {
                'status': '인터뷰',
                'description': '파일 업로드 기능은 있으나 서버 측 검증을 확인할 수 없습니다',
                'details': ['실제 파일 업로드 테스트를 통해 서버 측 검증 확인 필요']
            }
    
    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 오류 발생: {str(e)}',
            'details': []
        }