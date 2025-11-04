# modules/buffer_overflow.py
# -*- coding: utf-8 -*-
import time
from typing import Dict, Any

def test_buffer_overflow(target: str, session) -> Dict[str, Any]:
    """
    비파괴적 버퍼오버플로우 탐지(길이 증가로 인한 에러/응답 변화 감지)
    - 안전: 아주 길게 보내되 횟수·속도 제한
    """
    paths = ['/', '/search', '/login']  # 필요시 사용자 지정
    lengths = [128, 512, 1024, 2048]    # 점진적 길이
    details = []
    suspicious = False

    for p in paths:
        test_url = target.rstrip('/') + p
        baseline = None
        try:
            r = session.get(test_url, timeout=8)
            baseline = r.status_code
        except Exception as e:
            details.append(f"[baseline error] {test_url} 요청 실패: {e}")
            continue

        for L in lengths:
            payload = 'A' * L
            try:
                r2 = session.post(test_url, data={'q': payload}, timeout=8, allow_redirects=False)
                if r2.status_code >= 500:
                    suspicious = True
                    details.append(f"[에러발생] {test_url} 에서 길이 {L} 전송 후 상태 {r2.status_code}")
                    break
                # 본문 급변도 체크(간단)
                if r2.text and len(r2.text) > len((r.text or "")) * 5:
                    suspicious = True
                    details.append(f"[본문변화] {test_url} 길이 {L} -> 본문 급증")
                    break
            except Exception as e:
                details.append(f"[요청오류] {test_url} 길이 {L} 요청 실패: {e}")
            time.sleep(0.5)
    if suspicious:
        return {'status':'취약','description':'긴 입력에 대해 서버 오류/비정상 응답 발견','details':details}
    if details:
        return {'status':'인터뷰','description':'응답에 일부 이상징후가 있으나 확실치 않음','details':details}
    return {'status':'양호','description':'긴 입력에 대한 즉각적 오류 미발견','details':[]}
