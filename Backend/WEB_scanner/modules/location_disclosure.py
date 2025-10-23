#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modules/location_disclosure.py - 위치 공개 취약점 검사
"""

import re
from urllib.parse import urlparse, urljoin


def test_location_disclosure(target_url, session):
    """위치 공개 취약점 검사 (민감한 파일/디렉터리 노출)"""
    
    found_locations = []
    
    try:
        parsed = urlparse(target_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # 1. robots.txt 확인
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            robots_response = session.get(robots_url, timeout=10)
            
            if robots_response.status_code == 200:
                found_locations.append("robots.txt 존재 - 크롤러에 경로 정보 제공")
                
                # Disallow 경로 분석
                disallowed = re.findall(r'Disallow:\s*(/[^\s]+)', robots_response.text)
                if disallowed:
                    found_locations.append(f"  Disallow된 경로 {len(disallowed)}개 공개")
                    for path in disallowed[:5]:
                        found_locations.append(f"    - {path}")
        except:
            pass
        
        # 2. sitemap.xml 확인
        try:
            sitemap_url = urljoin(base_url, '/sitemap.xml')
            sitemap_response = session.get(sitemap_url, timeout=10)
            
            if sitemap_response.status_code == 200:
                urls = re.findall(r'<loc>(.*?)</loc>', sitemap_response.text)
                found_locations.append(f"sitemap.xml 존재 - {len(urls)}개의 URL 공개")
        except:
            pass
        
        # 3. 버전 관리 시스템 디렉터리
        vcs_checks = [
            ('/.git/', '.git 디렉터리'),
            ('/.svn/', '.svn 디렉터리'),
            ('/.hg/', '.hg 디렉터리 (Mercurial)'),
            ('/.bzr/', '.bzr 디렉터리 (Bazaar)'),
            ('/CVS/', 'CVS 디렉터리'),
        ]
        
        for path, desc in vcs_checks:
            try:
                vcs_url = urljoin(base_url, path)
                vcs_response = session.get(vcs_url, timeout=5)
                if vcs_response.status_code in [200, 301, 403]:  # 403도 존재하는 것
                    found_locations.append(f"{desc} 노출 - 소스 코드 유출 위험")
            except:
                pass
        
        # 4. 설정 파일 노출
        config_files = [
            '/.env',
            '/config.php',
            '/configuration.php',
            '/config.yml',
            '/config.json',
            '/settings.py',
            '/web.config',
            '/app.config',
            '/.htaccess',
            '/composer.json',
            '/package.json',
        ]
        
        for config_file in config_files:
            try:
                config_url = urljoin(base_url, config_file)
                config_response = session.get(config_url, timeout=5)
                if config_response.status_code == 200:
                    found_locations.append(f"설정 파일 노출: {config_file}")
            except:
                pass
        
        # 5. 백업 파일/디렉터리
        backup_paths = [
            '/backup/',
            '/backups/',
            '/old/',
            '/~/',
            '/bak/',
            '/_backup/',
            '/db_backup/',
        ]
        
        for backup_path in backup_paths:
            try:
                backup_url = urljoin(base_url, backup_path)
                backup_response = session.get(backup_url, timeout=5)
                if backup_response.status_code == 200:
                    if 'Index of' in backup_response.text or 'Directory' in backup_response.text:
                        found_locations.append(f"백업 디렉터리 노출: {backup_path}")
            except:
                pass
        
        # 6. 관리자 페이지/패널
        admin_paths = [
            '/admin/',
            '/administrator/',
            '/admin.php',
            '/admin/login',
            '/wp-admin/',
            '/administrator/index.php',
            '/admin/dashboard',
            '/manage/',
            '/management/',
            '/phpmyadmin/',
        ]
        
        for admin_path in admin_paths:
            try:
                admin_url = urljoin(base_url, admin_path)
                admin_response = session.get(admin_url, timeout=5, allow_redirects=False)
                if admin_response.status_code in [200, 301, 302]:
                    found_locations.append(f"관리자 경로 존재: {admin_path}")
            except:
                pass
        
        # 7. 테스트/개발 파일
        test_files = [
            '/test.php',
            '/test.html',
            '/phpinfo.php',
            '/info.php',
            '/test/',
            '/dev/',
            '/development/',
            '/staging/',
            '/debug.php',
        ]
        
        for test_file in test_files:
            try:
                test_url = urljoin(base_url, test_file)
                test_response = session.get(test_url, timeout=5)
                if test_response.status_code == 200:
                    found_locations.append(f"테스트/개발 파일 노출: {test_file}")
            except:
                pass
        
        # 8. 데이터베이스 파일
        db_files = [
            '/database.sql',
            '/db.sql',
            '/backup.sql',
            '/dump.sql',
            '/data.db',
            '/database.sqlite',
            '/db.sqlite3',
        ]
        
        for db_file in db_files:
            try:
                db_url = urljoin(base_url, db_file)
                db_response = session.get(db_url, timeout=5)
                if db_response.status_code == 200:
                    found_locations.append(f"데이터베이스 파일 노출: {db_file}")
            except:
                pass
        
        # 9. 문서/README 파일
        doc_files = [
            '/README.md',
            '/INSTALL.md',
            '/CHANGELOG.md',
            '/TODO.txt',
            '/readme.html',
            '/license.txt',
        ]
        
        for doc_file in doc_files:
            try:
                doc_url = urljoin(base_url, doc_file)
                doc_response = session.get(doc_url, timeout=5)
                if doc_response.status_code == 200:
                    found_locations.append(f"문서 파일 노출: {doc_file}")
            except:
                pass
        
        # 10. 서버 상태 페이지
        status_paths = [
            '/server-status',
            '/status',
            '/nginx_status',
            '/.well-known/',
        ]
        
        for status_path in status_paths:
            try:
                status_url = urljoin(base_url, status_path)
                status_response = session.get(status_url, timeout=5)
                if status_response.status_code == 200:
                    found_locations.append(f"서버 상태 페이지 노출: {status_path}")
            except:
                pass
        
        # 결과 평가
        if found_locations:
            critical_count = sum(1 for loc in found_locations if any(
                keyword in loc.lower() for keyword in ['.git', '.env', 'config', 'database', 'backup.sql']
            ))
            
            if critical_count > 0:
                return {
                    'status': '취약',
                    'description': f'민감한 위치/파일 {len(found_locations)}개가 공개되어 있습니다 (치명적: {critical_count}개)',
                    'details': found_locations
                }
            else:
                return {
                    'status': '인터뷰',
                    'description': f'{len(found_locations)}개의 위치 정보가 공개되어 있으나 추가 확인이 필요합니다',
                    'details': found_locations
                }
        else:
            return {
                'status': '양호',
                'description': '민감한 위치/파일 노출이 발견되지 않았습니다',
                'details': []
            }
    
    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 오류 발생: {str(e)}',
            'details': []
        }