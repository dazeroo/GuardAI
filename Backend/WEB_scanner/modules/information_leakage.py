#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modules/information_Leakage.py - 정보 누출 취약점 검사
"""

import re
from urllib.parse import urlparse, urljoin


def test_information_leakage(target_url, session):
    """정보 누출 취약점 검사"""
    
    vulnerabilities = []
    
    try:
        parsed = urlparse(target_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # 1. 서버 배너 정보 노출
        response = session.get(target_url, timeout=10)
        headers = response.headers
        
        if 'Server' in headers:
            server_info = headers['Server']
            vulnerabilities.append(f"서버 정보 노출: {server_info}")
        
        if 'X-Powered-By' in headers:
            powered_by = headers['X-Powered-By']
            vulnerabilities.append(f"기술 스택 정보 노출: {powered_by}")
        
        if 'X-AspNet-Version' in headers:
            asp_version = headers['X-AspNet-Version']
            vulnerabilities.append(f"ASP.NET 버전 노출: {asp_version}")
        
        # 2. HTML 주석에서 민감 정보 찾기
        response_text = response.text
        
        # 주석 추출
        comments = re.findall(r'<!--(.*?)-->', response_text, re.DOTALL)
        
        sensitive_keywords = [
            ('password', '비밀번호'),
            ('todo', 'TODO/작업 목록'),
            ('bug', '버그 정보'),
            ('admin', '관리자 정보'),
            ('secret', '비밀 정보'),
            ('key', 'API 키'),
            ('token', '토큰'),
            ('database', '데이터베이스 정보'),
            ('debug', '디버그 정보'),
            ('test', '테스트 정보'),
        ]
        
        for comment in comments:
            comment_lower = comment.lower()
            for keyword, desc in sensitive_keywords:
                if keyword in comment_lower:
                    preview = comment.strip()[:100].replace('\n', ' ')
                    vulnerabilities.append(f"주석에 {desc} 포함: {preview}...")
                    break
        
        # 3. JavaScript 파일에서 API 키나 토큰 찾기
        js_files = re.findall(r'<script[^>]*src=["\']([^"\']+\.js)["\']', response_text)
        
        for js_file in js_files[:5]:  # 최대 5개만
            try:
                js_url = urljoin(target_url, js_file)
                js_response = session.get(js_url, timeout=10)
                js_content = js_response.text
                
                # API 키 패턴
                api_patterns = [
                    (r'api[_-]?key\s*[:=]\s*["\']([a-zA-Z0-9_-]{20,})["\']', 'API 키'),
                    (r'access[_-]?token\s*[:=]\s*["\']([a-zA-Z0-9_-]{20,})["\']', 'Access Token'),
                    (r'secret\s*[:=]\s*["\']([a-zA-Z0-9_-]{20,})["\']', 'Secret'),
                ]
                
                for pattern, desc in api_patterns:
                    matches = re.findall(pattern, js_content, re.IGNORECASE)
                    if matches:
                        vulnerabilities.append(f"JavaScript에서 {desc} 노출 가능: {js_file}")
                        break
            except:
                pass
        
        # 4. 에러 메시지에서 정보 노출 확인
        error_patterns = [
            (r'Stack trace:', '스택 트레이스 노출'),
            (r'Exception:', '예외 정보 노출'),
            (r'Warning:', '경고 메시지 노출'),
            (r'Fatal error:', '치명적 오류 노출'),
            (r'MySQL error:', 'MySQL 오류 노출'),
            (r'PostgreSQL error:', 'PostgreSQL 오류 노출'),
            (r'ODBC error:', 'ODBC 오류 노출'),
            (r'at line \d+', '코드 라인 번호 노출'),
            (r'in /[^\s]+\.php', '파일 경로 노출'),
            (r'in C:\\[^\s]+', 'Windows 경로 노출'),
        ]
        
        for pattern, desc in error_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                vulnerabilities.append(f"에러 메시지에서 {desc}")
        
        # 5. robots.txt 확인
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            robots_response = session.get(robots_url, timeout=10)
            
            if robots_response.status_code == 200:
                disallowed_paths = re.findall(r'Disallow:\s*(/[^\s]+)', robots_response.text)
                if disallowed_paths:
                    sensitive_paths = [p for p in disallowed_paths if any(
                        keyword in p.lower() for keyword in ['admin', 'backup', 'private', 'secret']
                    )]
                    if sensitive_paths:
                        vulnerabilities.append(f"robots.txt에 민감한 경로 노출: {', '.join(sensitive_paths[:3])}")
        except:
            pass
        
        # 6. .git, .svn 등 버전 관리 디렉터리 노출
        vcs_paths = [
            '/.git/config',
            '/.git/HEAD',
            '/.svn/entries',
            '/.hg/requires',
            '/.bzr/branch/branch.conf',
        ]
        
        for vcs_path in vcs_paths:
            try:
                vcs_url = urljoin(base_url, vcs_path)
                vcs_response = session.get(vcs_url, timeout=5)
                if vcs_response.status_code == 200:
                    vulnerabilities.append(f"버전 관리 디렉터리 노출: {vcs_path}")
            except:
                pass
        
        # 7. 백업 파일 노출
        if parsed.path:
            backup_extensions = ['.bak', '.backup', '.old', '.tmp', '~']
            for ext in backup_extensions:
                try:
                    backup_url = target_url + ext
                    backup_response = session.get(backup_url, timeout=5)
                    if backup_response.status_code == 200:
                        vulnerabilities.append(f"백업 파일 노출: {backup_url}")
                        break
                except:
                    pass
        
        # 8. 디버그 모드 활성화 확인
        debug_indicators = [
            'debug mode',
            'debug=true',
            'development mode',
            '__debug__',
            'var_dump',
            'print_r',
        ]
        
        for indicator in debug_indicators:
            if indicator in response_text.lower():
                vulnerabilities.append(f"디버그 모드 활성화 가능성: '{indicator}' 발견")
                break
        
        # 9. phpinfo 노출 확인
        try:
            phpinfo_paths = ['/phpinfo.php', '/info.php', '/test.php']
            for path in phpinfo_paths:
                phpinfo_url = urljoin(base_url, path)
                phpinfo_response = session.get(phpinfo_url, timeout=5)
                if 'phpinfo()' in phpinfo_response.text or 'PHP Version' in phpinfo_response.text:
                    vulnerabilities.append(f"phpinfo() 페이지 노출: {path}")
                    break
        except:
            pass
        
        # 결과 평가
        if vulnerabilities:
            return {
                'status': '취약',
                'description': f'{len(vulnerabilities)}개의 정보 누출이 발견되었습니다',
                'details': vulnerabilities
            }
        else:
            return {
                'status': '양호',
                'description': '정보 누출이 발견되지 않았습니다',
                'details': []
            }
    
    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 오류 발생: {str(e)}',
            'details': []
        }