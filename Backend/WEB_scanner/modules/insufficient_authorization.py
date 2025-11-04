# modules/authorization.py
# -*- coding: utf-8 -*-
import time
from typing import Dict, Any

def test_insufficient_authorization(target: str, session) -> Dict[str, Any]:
    """
    간단한 인가(Authorization) 검사
    - 권한이 필요한 URL(관리자 API 등)에 대해 비인증 요청과 인증 요청의 차이를 비교
    - session은 인증된 세션이 될수도 있고, 비인증 상태일수도 있음.
    """
    protected_paths = ['/admin', '/api/admin/data', '/user/profile']
    details = []
    issues = []

    for p in protected_paths:
        url = target.rstrip('/') + p
        try:
            # 익명(새 세션)
            anon = session.__class__()  # 같은 세션 클래스
            anon.headers.update(session.headers)
            r_anon = anon.get(url, timeout=8, allow_redirects=False)
            r_auth = session.get(url, timeout=8, allow_redirects=False)
            if r_anon.status_code == 200 and r_auth.status_code == 200:
                issues.append(f"{url} 에 대해 인증 없이도 200 응답(인가 누락 가능성)")
            elif r_anon.status_code == 403 and r_auth.status_code == 200:
                details.append(f"{url} : 인증 필요(정상)")
            else:
                details.append(f"{url} : anon={r_anon.status_code}, auth={r_auth.status_code}")
        except Exception as e:
            details.append(f"[요청오류] {url}: {e}")
        time.sleep(0.3)

    if issues:
        return {'status':'취약','description':'인가 제어 부족 의심','details':issues+details}
    if details:
        return {'status':'인터뷰','description':'인가 검사 결과 일부 관찰됨','details':details}
    return {'status':'양호','description':'기본 인가 검사 통과','details':[]}
