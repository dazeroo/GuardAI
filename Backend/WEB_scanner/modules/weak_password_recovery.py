# modules/weak_password_recovery.py
# -*- coding: utf-8 -*-
import re
import time
from typing import Dict, Any

def test_weak_password_recovery(target: str, session) -> Dict[str, Any]:
    reset_path = '/password-reset'  # 실제 비밀번호 재설정 요청 엔드포인트로 변경 필요
    details = []
    issues = []
    is_vulnerable_to_web_output = False # 웹사이트 화면 바로 출력 취약점 플래그

    # (1) 계정 열거 테스트: 존재하는 이메일 vs 존재하지 않는 이메일 메시지 차이
    try:
        url = target.rstrip('/') + reset_path
        
        # 실제 환경에 존재하는 이메일과 존재하지 않는 이메일로 대체해야 정확함
        resp_nonexist = session.post(url, data={'email':'no-such-user@example.invalid'}, timeout=8)
        resp_exist = session.post(url, data={'email':'admin@example.com'}, timeout=8)
        
        t_nonexist = (resp_nonexist.text or "").lower()
        t_exist = (resp_exist.text or "").lower()
        
        if ('no account' in t_nonexist or 'not found' in t_nonexist) and ('check your email' in t_exist or 'reset link' in t_exist):
            issues.append("계정 열거 가능: 응답 메시지 차이로 계정 존재 여부 유추 가능")
            details.append("계정 열거 방지가 미흡하여 공격자가 유효한 계정 목록을 확보할 수 있음.")
    except Exception as e:
        details.append(f"[요청오류] 재설정 엔드포인트 검사 실패: {e}")

    # (2) 토큰/링크 노출 검사: 웹 사이트 화면에 바로 출력되는지 확인
    # 이는 '취약: 웹 사이트 화면에 바로 출력 시' 기준을 판단하는 가장 중요한 로직입니다.
    try:
        # 응답 본문에 토큰, 링크, 임시 비밀번호가 바로 노출되는지 확인
        r = session.post(url, data={'email':'test@example.com'}, timeout=8)
        body = (r.text or "").lower()
        
        # 토큰/링크/비밀번호 패턴 노출 지표
        exposure_indicators = ['reset link', 'token', 'password reset link', 'temporary password']
        
        if any(indicator in body for indicator in exposure_indicators):
            issues.append("재설정 정보가 웹 화면에 노출됨: 토큰, 링크, 임시 비밀번호 중 하나가 응답 본문에 포함")
            details.append("취약: 패스워드 재설정 정보가 웹 화면에 바로 출력되어 중간자 공격이나 단순 요청으로 노출 위험")
            is_vulnerable_to_web_output = True
    except Exception:
        pass

    # 최종 결과 판단
    if issues or is_vulnerable_to_web_output:
        # '웹 사이트 화면 바로 출력' 등의 명확한 취약점 발견 시
        return {'status':'취약',
                'description':'비밀번호 재설정 흐름에서 정보 노출/예측 가능성 발견',
                'details':details + issues}
    
    # 명확한 취약점은 없지만, CII 기준의 난수성/안전 전송은 자동 확인 불가
    
    # CII 기준: '패스워드 재설정 시 난수를 사용하여 재설정되고 인증된 사용자 메일이나 SMS로 전송' 여부는
    # 자동 검사가 불가능하므로, '양호' 대신 '인터뷰'를 반환하여 수동 확인을 요청합니다.
    details.append("난수성 및 이메일/SMS 전송 여부 (CII 기준)는 수동 확인이 필요합니다.")
    
    return {'status':'인터뷰',
            'description':'비밀번호 재설정 기본 검사 통과. 난수 사용 및 안전 전송 여부 확인 필요',
            'details':details}
