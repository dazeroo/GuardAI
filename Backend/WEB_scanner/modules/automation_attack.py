# modules/automation_attack.py
# -*- coding: utf-8 -*-
"""
자동화 공격
- 캡차/recaptcha 탐지  (data-sitekey, g-recaptcha 등)
- User-Agent 기반 검증 탐지: 정상 UA vs 빈 UA/봇 UA 비교
- Rate-limit 탐지: 짧은 burst 요청으로 429 또는 메시지 확인 (안전한 횟수로 제한)
"""

import time
import re
from typing import Dict, Any
from bs4 import BeautifulSoup
import requests

# 안전한 기본 설정
BURST_REQUESTS = 6          # rate-limit 검사 시 보낼 최대 요청 수 (작게 유지)
BURST_DELAY = 0.5           # 연속 요청 간 대기(초)
UA_TEST_TIMEOUT = 8         # UA 테스트 타임아웃
GENERAL_TIMEOUT = 10        # 기본 요청 타임아웃


def _detect_captcha_from_html(text: str) -> bool:
    """HTML 텍스트에서 캡차 관련 요소를 탐지"""
    if not text:
        return False
    t = text.lower()
    # 흔한 키워드, 태그, 스크립트, 속성
    checks = [
        'captcha', 'recaptcha', 'g-recaptcha', 'grecaptcha',
        'data-sitekey', '/recaptcha/', 'www.google.com/recaptcha',
        'h-captcha', 'data-hcaptcha-widget', 'solvemedia',
        'cloudflare', 'cf-chl-bypass', 'captcha-form'
    ]
    for c in checks:
        if c in t:
            return True
    # DOM에서 <iframe>이나 div로 표시되는 경우 검사
    try:
        soup = BeautifulSoup(text, 'html.parser')
        if soup.find('div', class_=re.compile(r'.*captcha.*')) or soup.find('div', id=re.compile(r'.*captcha.*')):
            return True
        if soup.find('iframe', src=re.compile(r'.*recaptcha.*|.*captcha.*')):
            return True
    except Exception:
        pass
    return False


def _detect_rate_limit_by_burst(session: requests.Session, url: str) -> bool:
    """
    짧은 burst 요청으로 429 또는 'too many requests' 등 rate-limit 징후 확인
    안전을 위해 요청 수/간격을 작게 제한함.
    """
    count_429 = 0
    count_msg = 0
    for i in range(BURST_REQUESTS):
        try:
            r = session.get(url, timeout=GENERAL_TIMEOUT)
            status = r.status_code
            text = (r.text or "").lower()
            if status == 429:
                count_429 += 1
            if 'too many requests' in text or 'rate limit' in text:
                count_msg += 1
        except requests.RequestException:
            # 네트워크 문제는 무시하고 다음으로
            pass
        time.sleep(BURST_DELAY)
    return (count_429 > 0) or (count_msg > 0)


def _detect_ua_blocking(session: requests.Session, url: str) -> bool:
    """
    User-Agent 기반 차단 / 검증이 있는지 비교 검사
    - 정상 UA로 요청한 응답 vs 빈 UA 또는 명백한 bot UA로 요청한 응답 비교
    - 응답 상태코드 또는 주요 본문 변화가 있으면 서버가 UA에 반응하는 것으로 간주
    """
    try:
        # 정상 요청 (이미 세션의 헤더 사용)
        r_normal = session.get(url, timeout=UA_TEST_TIMEOUT)
        text_normal = (r_normal.text or "")[:1000]
        status_normal = r_normal.status_code
    except requests.RequestException:
        return False  # 정상 요청 불가시 UA 검사 불가

    # 테스트 1: 빈 User-Agent
    headers_empty = dict(session.headers)
    headers_empty['User-Agent'] = ''
    try:
        r_empty = session.get(url, headers=headers_empty, timeout=UA_TEST_TIMEOUT)
        text_empty = (r_empty.text or "")[:1000]
        status_empty = r_empty.status_code
    except requests.RequestException:
        return False

    # 테스트 2: 명백한 봇 User-Agent
    headers_bot = dict(session.headers)
    headers_bot['User-Agent'] = 'curl/7.68.0'
    try:
        r_bot = session.get(url, headers=headers_bot, timeout=UA_TEST_TIMEOUT)
        text_bot = (r_bot.text or "")[:1000]
        status_bot = r_bot.status_code
    except requests.RequestException:
        return False

    # 상태 코드 변화 또는 본문 변화가 있으면 UA 기반 차단/검증 가능성
    if status_normal != status_empty or status_normal != status_bot:
        return True
    if text_normal != text_empty or text_normal != text_bot:
        # 단순한 차이도 서버가 UA에 반응했을 가능성
        return True
    return False


def test_automation_attack(target: str, session) -> Dict[str, Any]:
    """
    자동화 공격 방어 점검
    반환 형식: {'status', 'description', 'details'}
    """
    findings = []
    details = []

    try:
        # 초기 페이지 요청
        try:
            resp = session.get(target, timeout=GENERAL_TIMEOUT)
            text = (resp.text or "")
        except requests.RequestException as e:
            return {
                'status': '인터뷰',
                'description': f'대상에 요청 불가: {e}',
                'details': []
            }

        # 1) CAPTCHA / reCAPTCHA 탐지
        if _detect_captcha_from_html(text):
            details.append("CAPTCHA/recaptcha 요소 발견 (HTML 내 data-sitekey 등).")
        else:
            findings.append("CAPTCHA 또는 reCAPTCHA 요소 미존재")

        # 2) Rate limit 탐지 (burst 요청)
        rate_limited = _detect_rate_limit_by_burst(session, target)
        if rate_limited:
            details.append("짧은 연속 요청에서 429 또는 rate-limit 메시지 탐지됨.")
        else:
            findings.append("Rate Limit(429 등) 징후 미발견 (짧은 burst 테스트 기준)")

        # 3) User-Agent 검증 여부 검사
        try:
            ua_blocking = _detect_ua_blocking(session, target)
            if ua_blocking:
                details.append("User-Agent 변경 시 응답 차이 존재: UA 기반 검증/차단 가능성.")
            else:
                # UA 차이 없음 -> 방어 없음(또는 UA 기반 필터 없음)
                findings.append("User-Agent 기반 차단/검증 징후 미발견")
        except Exception:
            findings.append("User-Agent 검사 불완전 (요청 실패)")

        # 평가: findings(문제징후) 개수 기준으로 판정
        # findings는 '문구 기반 부재' 항목을 모아둔 리스트
        if len(findings) >= 2:
            status = '취약'
            description = '자동화 공격 방어 기능이 전반적으로 누락됨'
        elif len(findings) == 1:
            status = '인터뷰'
            description = '일부 자동화 공격 방어 기능이 부족함'
        else:
            status = '양호'
            description = '자동화 방어(캡차/Rate-limit/UA 검사)에서 명백한 취약 징후 없음'

        return {
            'status': status,
            'description': description,
            'details': details or findings
        }

    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 예외 발생: {e}',
            'details': []
        }
