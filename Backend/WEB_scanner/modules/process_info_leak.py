# modules/process_info_leak.py
# -*- coding: utf-8 -*-
from typing import Dict, Any

def test_process_info_leak(target: str, session) -> Dict[str, Any]:
    endpoints = ['/.env', '/server-status', '/phpinfo.php', '/status', '/.git/config']
    headers = ['server', 'x-powered-by', 'x-debug-token']
    details = []
    issues = []

    try:
        r = session.get(target, timeout=8)
        for h in headers:
            if h in r.headers:
                val = r.headers.get(h)
                issues.append(f"헤더 노출: {h} -> {val}")
        for e in endpoints:
            url = target.rstrip('/') + e
            try:
                rr = session.get(url, timeout=6, allow_redirects=False)
                if rr.status_code == 200 and len((rr.text or ""))>0:
                    issues.append(f"민감 엔드포인트 접근 가능: {url} (상태 {rr.status_code})")
            except Exception:
                pass
    except Exception as e:
        return {'status':'인터뷰','description':f'요청 실패: {e}','details':[]}

    if issues:
        return {'status':'취약','description':'서버/프로세스 정보 노출 가능성 발견','details':issues}
    return {'status':'양호','description':'프로세스/서버 정보 노출 없음(기본 체크)','details':[]}
