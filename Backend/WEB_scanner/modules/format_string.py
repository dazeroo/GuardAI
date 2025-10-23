# modules/format_string.py
# -*- coding: utf-8 -*-
import re
import time
from typing import Dict, Any

def test_format_string(target: str, session) -> Dict[str, Any]:
    paths = ['/', '/search', '/comment']
    payloads = ['%x.%x.%x', '%s%s%s', '{0}{1}{2}', '%08x' ]
    details = []
    vuln = False

    for p in paths:
        url = target.rstrip('/') + p
        try:
            base = session.get(url, timeout=6)
            base_text = (base.text or "")[:2000]
        except Exception as e:
            details.append(f"[기본요청실패] {url}: {e}")
            continue
        for pl in payloads:
            try:
                r = session.post(url, data={'input': pl}, timeout=6)
                text = (r.text or "").lower()
                # 예: 페이로드 자체가 반사되거나 메모리 형식 텍스트 노출
                if pl in text:
                    vuln = True
                    details.append(f"[반사됨] {url} 에서 페이로드 반사: {pl}")
                    break
                # 에러 메시지 내 format 관련 키워드
                if re.search(r'format.*error|printf|exception|segmentation fault', text, re.I):
                    vuln = True
                    details.append(f"[에러노출] {url} 에서 포맷/에러 메시지 탐지")
                    break
            except Exception as e:
                details.append(f"[요청오류] {url} payload={pl} 에러: {e}")
            time.sleep(0.3)
    if vuln:
        return {'status':'취약','description':'포맷 스트링 취약 의심','details':details}
    if details:
        return {'status':'인터뷰','description':'포맷 스트링 검사 중 일부 이상징후','details':details}
    return {'status':'양호','description':'명백한 포맷 스트링 징후 미발견','details':[]}
