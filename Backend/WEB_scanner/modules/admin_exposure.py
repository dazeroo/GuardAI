# modules/admin_exposure.py
# -*- coding: utf-8 -*-
"""
관리자 페이지 노출 진단
- 1) 일반적인 관리자 경로 접근 가능 여부 확인 (/admin, /wp-admin 등)
- 2) 흔한 포트(80,443,8080,8443 등)로 접근 시도하여 노출 여부 확인
- 3) 관리자 로그인 폼에 대해 제한된 기본 관리자 계정으로 로그인 시도 (작은 샘플만)
- 4) 로그인 후 식별된 하위 페이지 URL을 새 세션에서 인증 없이 접근 가능한지 확인
"""

import requests
from typing import Dict, Any, List
from urllib.parse import urlparse, urlunparse, quote, urljoin
from bs4 import BeautifulSoup
import time

COMMON_ADMIN_PATHS = [
    "/admin", "/administrator", "/wp-admin", "/cms", "/login",
    "/manage", "/backend", "/console", "/system", "/controlpanel",
    "/manager", "/master"
]

# 안전을 위해 매우 제한된 기본 계정 샘플 (테스트용)
DEFAULT_CREDENTIALS = [
    ("admin", "admin"),
    ("admin", "password"),
    ("admin", "123456"),
    ("administrator", "admin"),
    ("admin", "wordpress"),
    ("manager", "manager")
]

# 흔히 관리자용으로 쓰이는 포트(테스트 범위)
COMMON_ADMIN_PORTS = [80, 443, 7001, 8080, 8443, 8000, 8888, 9000]


def _is_login_page_text(text: str) -> bool:
    """응답 텍스트가 로그인 페이지로 보이는지 간단히 판단"""
    if not text:
        return False
    t = text.lower()
    keywords = ['login', 'username', 'user', 'password', 'wp-login', '관리자', '로그인']
    return any(k in t for k in keywords)


def _find_login_form(soup: BeautifulSoup) -> Dict:
    """
    폼에서 로그인 폼을 유추:
    반환: {'action': url_or_empty, 'method': 'post'/'get', 'user_field': name, 'pass_field': name}
    """
    forms = soup.find_all('form')
    for form in forms:
        inputs = form.find_all('input')
        uname = None
        pword = None
        for inp in inputs:
            itype = (inp.get('type') or '').lower()
            name = inp.get('name') or inp.get('id') or ''
            lname = (inp.get('placeholder') or '').lower()
            if itype in ('password',):
                pword = name
            # username-like detection
            if itype in ('text', 'email') or 'user' in name.lower() or 'id' in name.lower() or 'login' in name.lower() or 'email' in name.lower() or 'userid' in name.lower() or 'username' in name.lower() or 'id' in lname or 'user' in lname:
                if not uname:
                    uname = name
        if pword:
            action = form.get('action') or ''
            method = (form.get('method') or 'post').lower()
            return {'action': action, 'method': method, 'user_field': uname or '', 'pass_field': pword}
    return {}


def _submit_login(session: requests.Session, action_url: str, method: str, user_field: str, pass_field: str, username: str, password: str, timeout: int = 10):
    """
    로그인 폼 제출 보조: 성공 여부를 raw response로 반환
    """
    payload = {}
    if user_field:
        payload[user_field] = username
    else:
        # 만약 user_field를 못 찾았으면 흔한 파라미터명 시도
        payload.update({'username': username, 'user': username, 'login': username})

    payload[pass_field] = password

    try:
        if method == 'post':
            resp = session.post(action_url, data=payload, timeout=timeout, allow_redirects=True)
        else:
            resp = session.get(action_url, params=payload, timeout=timeout, allow_redirects=True)
        return resp
    except requests.RequestException:
        return None


def test_admin_exposure(target: str, session) -> Dict[str, Any]:
    """
    관리자 페이지 노출 및 인증 우회 점검
    Returns:
      {'status': '양호'|'취약'|'인터뷰', 'description': str, 'details': [str,...]}
    """
    details: List[str] = []
    found_admin_pages: List[str] = []
    login_success_info: List[str] = []
    accessible_without_auth: List[str] = []

    # 기본 체크: 일반적인 관리자 경로
    try:
        for path in COMMON_ADMIN_PATHS:
            test_url = target.rstrip("/") + path
            try:
                resp = session.get(test_url, timeout=8, allow_redirects=False)
            except requests.RequestException as e:
                details.append(f"[경로 체크] {test_url} 요청 실패: {e}")
                continue

            text = (resp.text or "").lower() if resp.text else ""
            if resp.status_code in (200, 302) and _is_login_page_text(text):
                found_admin_pages.append(test_url)
                details.append(f"[경로 체크] 관리자 로그인 페이지 추정됨: {test_url} (상태코드 {resp.status_code})")

        # 단계2: 흔한 관리자 포트로 접속 시도 (도메인에 포트 부착)
        parsed = urlparse(target)
        host = parsed.hostname
        scheme = parsed.scheme or 'https'
        if host:
            for port in COMMON_ADMIN_PORTS:
                # 포트가 이미 URL에 있으면 건너뛰기
                if parsed.port == port:
                    continue
                # scheme을 http/https로 바꿔가며 시도 (443->https, 80->http 등)
                test_scheme = 'https' if port in (443, 8443) else 'http'
                netloc = f"{host}:{port}"
                port_url = urlunparse((test_scheme, netloc, '/', '', '', ''))
                try:
                    r = session.get(port_url, timeout=5, allow_redirects=False)
                    if r.status_code in (200, 302) and _is_login_page_text(r.text):
                        found_admin_pages.append(port_url)
                        details.append(f"[포트 체크] 포트 노출된 관리자 페이지 추정: {port_url} (상태코드 {r.status_code})")
                except requests.RequestException:
                    # 포트 닫힘 또는 차단된 경우 무시
                    continue

        # 단계3: 로그인 폼을 찾아서 제한된 기본 계정으로 시도 (최대 N개)
        MAX_CREDENTIAL_TRIES = 3
        cred_attempts = 0
        for admin_page in list(dict.fromkeys(found_admin_pages)):  # 중복 제거
            if cred_attempts >= MAX_CREDENTIAL_TRIES:
                break
            # GET 페이지 및 파싱
            try:
                r = session.get(admin_page, timeout=8)
            except requests.RequestException:
                continue
            soup = BeautifulSoup(r.text or "", 'html.parser')
            form_info = _find_login_form(soup)
            if not form_info:
                details.append(f"[로그인 탐지] 로그인 폼을 찾지 못함: {admin_page}")
                continue

            action = form_info.get('action') or ''
            # action이 상대경로이면 절대화
            action_url = urljoin(admin_page, action) if action else admin_page
            method = form_info.get('method', 'post')
            user_field = form_info.get('user_field', '')
            pass_field = form_info.get('pass_field', '')

            # 제한된 기본 계정들로 시도 (안전장치: 짧은 목록, 재시도 제한)
            for username, password in DEFAULT_CREDENTIALS:
                if cred_attempts >= MAX_CREDENTIAL_TRIES:
                    break
                cred_attempts += 1
                # 새 세션을 사용해 로그인 시도 (원본 세션의 인증 상태를 오염시키지 않음)
                test_sess = requests.Session()
                test_sess.headers.update(session.headers)
                test_sess.verify = session.verify
                resp = _submit_login(test_sess, action_url, method, user_field, pass_field, username, password, timeout=8)
                time.sleep(0.5)  # 안전한 속도
                if resp is None:
                    continue
                # 로그인 성공 판단: 리다이렉트, 대시보드/로그아웃 키워드 존재, 세션에 쿠키가 발급되는지 등
                success = False
                if resp.history and any(300 <= h.status_code < 400 for h in resp.history):
                    success = True
                body = (resp.text or "").lower()
                if any(k in body for k in ['dashboard', 'logout', 'sign out', '관리자', 'wp-admin', 'welcome']):
                    success = True
                # 쿠키 기준(간단): 세션 쿠키가 발급되었는지
                if test_sess.cookies:
                    # 일반적인 로그인 쿠키가 생성되면 의심
                    success = success or True

                if success:
                    login_success_info.append(f"{admin_page} 에서 기본계정 로그인 성공 가능: {username}/{password} (action: {action_url})")
                    details.append(f"[로그인 성공] {admin_page} 에서 기본계정으로 로그인 성공 시도: {username}/{password}")
                    # 로그인된 세션에서 하위 경로 식별
                    try:
                        dash_resp = test_sess.get(action_url, timeout=8)
                        # 단순히 페이지 내 링크들을 수집
                        dash_soup = BeautifulSoup(dash_resp.text or "", 'html.parser')
                        links = set()
                        for a in dash_soup.find_all('a', href=True):
                            href = a['href']
                            if href.startswith('/') or href.startswith(admin_page):
                                links.add(urljoin(admin_page, href))
                        # 이제 step4: 새 세션(인증 없음)으로 위 링크 접근 시도
                        for l in list(links)[:10]:  # 안전상 최대 10개만 검사
                            anon = requests.Session()
                            anon.headers.update(session.headers)
                            anon.verify = session.verify
                            try:
                                anon_resp = anon.get(l, timeout=6, allow_redirects=False)
                                # 인증 없이도 200이면 접근 가능
                                if anon_resp.status_code == 200:
                                    accessible_without_auth.append(l)
                                    details.append(f"[인증 우회 가능] 인증 없이 접근 가능한 서브페이지: {l} (상태 {anon_resp.status_code})")
                            except requests.RequestException:
                                continue
                    except Exception:
                        pass
                    # 로그인 성공 발견 후엔 추가 크리덴셜 시도 중단 (정책)
                    break
                else:
                    details.append(f"[로그인 실패] {admin_page} 에서 기본계정 시도 실패: {username}/{password}")
            # 다음 admin_page로 이동

        # 평가 및 반환 정리
        if found_admin_pages or login_success_info or accessible_without_auth:
            # 우선 취약으로 분류하고 상세히 기술(심각도는 상황에 따라 판단)
            desc_parts = []
            if found_admin_pages:
                desc_parts.append(f"발견된 관리자/로그인 페이지: {len(found_admin_pages)}개")
            if login_success_info:
                desc_parts.append(f"기본계정으로 로그인 가능한 페이지: {len(login_success_info)}개")
            if accessible_without_auth:
                desc_parts.append(f"인증 없이 접근 가능한 내부 페이지: {len(accessible_without_auth)}개")

            return {
                'status': '취약',
                'description': '; '.join(desc_parts),
                'details': details
            }

        # 아무 것도 발견되지 않음
        return {
            'status': '양호',
            'description': '관리자 페이지 접근 및 기본 계정/인증 우회 사례 미발견',
            'details': details
        }

    except requests.exceptions.RequestException as e:
        return {
            'status': '인터뷰',
            'description': f'요청 중 오류 발생: {str(e)}',
            'details': details
        }
