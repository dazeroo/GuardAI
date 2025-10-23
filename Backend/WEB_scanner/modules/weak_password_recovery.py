# modules/weak_password_recovery.py
# -*- coding: utf-8 -*-
import re
import time
from typing import Dict, Any

def test_weak_password_recovery(target: str, session) -> Dict[str, Any]:
    reset_path = '/password-reset'  # 또는 /wp-login.php?action=lostpassword 등
    details = []
    issues = []

    # (1) 계정 열거 테스트: 존재하는 이메일 vs 존재하지 않는 이메일 메시지 차이
    try:
        url = target.rstrip('/') + reset_path
        resp1 = session.post(url, data={'email':'no-such-user@example.invalid'}, timeout=8)
        resp2 = session.post(url, data={'email':'admin@example.com'}, timeout=8)
        t1 = (resp1.text or "").lower()
        t2 = (resp2.text or "").lower()
        if ('no account' in t1 or 'not found' in t1) and ('check your email' in t2 or 'reset link' in t2):
            issues.append("비밀번호 재설정 요청에 계정 존재 여부가 노출되어 계정 열거 가능")
            details.append("응답 메시지 차이로 계정 존재 여부 유추 가능")
    except Exception as e:
        details.append(f"[요청오류] 재설정 엔드포인트 검사 실패: {e}")

    # (2) 토큰/링크 노출 검사: 일부 앱은 리셋 링크를 바로 응답에 포함
    # (실제로 이메일 확인을 요구하는 경우가 많아 처리 결과 다름)
    # 간단 체크만 수행(응답 본문에 token 또는 reset link 키워드 존재)
    try:
        r = session.post(url, data={'email':'test@example.com'}, timeout=8)
        body = (r.text or "").lower()
        if 'reset link' in body or 'token' in body or 'password reset' in body:
            details.append("응답에 리셋 링크/토큰 관련 문구 존재(이메일 기반이면 수동 확인 권장)")
    except Exception:
        pass

    if issues:
        return {'status':'취약','description':'비밀번호 재설정 흐름에서 정보 노출/예측 가능성 발견','details':details}
    if details:
        return {'status':'인터뷰','description':'비밀번호 재설정 검사 중 일부 의심 항목','details':details}
    return {'status':'양호','description':'비밀번호 재설정 기본 검사 통과','details':[]}
