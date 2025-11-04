# modules/location_disclosure.py - 위치 공개 취약점 진단 (CII 기준)
# -*- coding: utf-8 -*-
import re
from urllib.parse import urlparse, urljoin
from typing import Dict, Any, List


def test_location_disclosure(target_url: str, session) -> Dict[str, Any]:
    """
    위치 공개 취약점 검사 (CII 점검 방법 Step 1, 2 반영)
    - 불필요한 확장자 파일, 샘플 페이지/디렉터리 존재 여부 확인
    """
    
    found_locations: List[str] = []
    
    # Step 1) 불필요한 확장자 파일 (백업, 설정 파일 등) 확인
    unnecessary_extensions = [
        '.bak', '.backup', '.orig', '.old', '.zip', '.log', 
        '.sql', '.new', '.txt', '.tmp', '.temp', '~', '.conf', '.cfg' 
    ]
    
    # 타겟 URL의 경로를 기반으로 파일명 추정 (예: /index.php -> /index.php.bak)
    parsed = urlparse(target_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    test_files_base = [parsed.path] if parsed.path and parsed.path != '/' else ['/index.php', '/default.html']
    
    
    # Step 2) 각종 샘플 페이지/디렉터리 확인
    sample_paths = [
        '/cgi-bin/', '/manual/', '/usage/', '/iisstart.htm', '/iishelp/', 
        '/iisaAdmin/', '/_vti_bin/', '/_vti_pvt/', '/phpinfo.php', 
        '/info.php', '/test.php', '/examples/', '/scripts/', '/servlet/'
    ]
    
    # ------------------ 검사 로직 시작 ------------------
    
    try:
        # 1. 불필요한 확장자 파일 체크
        for base_file in test_files_base:
            for ext in unnecessary_extensions:
                # /index.php + .bak -> /index.php.bak
                test_path = base_file + ext if base_file != '/' else base_file + 'index' + ext
                
                try:
                    test_url = urljoin(base_url, test_path)
                    response = session.get(test_url, timeout=5, allow_redirects=False)
                    
                    # 200 OK 또는 디렉터리 인덱싱이 활성화된 경우 (200 + Index of)
                    if response.status_code == 200:
                        found_locations.append(f"불필요한 확장자 파일 노출: {test_path} (상태 200)")
                    elif response.status_code == 403:
                        # 403도 파일 존재 가능성이 높지만, 여기서는 200에 집중
                        pass 
                except Exception:
                    continue

        # 2. 샘플 페이지 및 디렉터리 체크
        for path in sample_paths:
            try:
                test_url = urljoin(base_url, path)
                response = session.get(test_url, timeout=5, allow_redirects=False)
                
                # 200 OK 응답이면 노출로 간주
                if response.status_code == 200:
                    found_locations.append(f"샘플/개발 경로 노출: {path} (상태 200)")
                    
                # 서버 상태 페이지 텍스트 포함 여부 확인 (샘플 페이지의 일종)
                text = (response.text or "").lower()
                if 'apache test page' in text or 'iis start' in text or 'phpinfo()' in text:
                    found_locations.append(f"샘플/개발 페이지 내용 확인: {path}")

            except Exception:
                continue

        # ------------------ 결과 평가 ------------------
        
        if found_locations:
            return {
                'status': '취약',
                'description': f'불필요 파일 또는 샘플 경로 {len(found_locations)}개가 공개되어 있음',
                'details': found_locations
            }
        else:
            return {
                'status': '양호',
                'description': '불필요 파일 및 샘플 경로 노출 없음 (기본 검사 통과)',
                'details': []
            }
    
    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 오류 발생: {str(e)}',
            'details': [str(e)]
        }
