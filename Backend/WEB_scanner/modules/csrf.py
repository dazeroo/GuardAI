# modules/csrf_injection.py
# -*- coding: utf-8 -*-


import re
import requests
from typing import Dict, List, Any
from urllib.parse import urljoin
from bs4 import BeautifulSoup


class SessionCSRFScanner:
    """세션 기반 CSRF 스캐너"""

    def __init__(self, session, timeout: int = 10):
        self.session = session
        self.timeout = timeout
        self.vulnerabilities = []

        self.csrf_token_names = [
            'csrf_token', 'csrftoken', 'csrf', '_csrf',
            'token', '_token', 'authenticity_token',
            'anti_csrf', 'xsrf_token', 'xsrf', '_xsrf',
            'csrf_protection', 'security_token'
        ]

    def scan(self, url: str) -> List[Dict[str, Any]]:
        """지정된 URL의 폼을 분석하여 CSRF 취약 여부 확인"""
        self.vulnerabilities = []
        try:
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            forms = soup.find_all('form')

            for form in forms:
                self._analyze_form(form, url)

        except requests.exceptions.RequestException as e:
            print(f"[!] {url} 요청 중 오류 발생: {str(e)}")

        return self.vulnerabilities

    def _analyze_form(self, form, base_url: str):
        """폼 내 CSRF 방어 존재 여부 및 검증 로직 확인"""
        action = form.get('action', '')
        method = form.get('method', 'get').upper()
        if method == 'GET':  # GET은 상태변경 없음
            return

        action_url = urljoin(base_url, action)
        has_token = self._has_csrf_token(form)
        inputs = form.find_all(['input', 'textarea', 'select'])
        form_data = {
            inp.get('name'): inp.get('value', '')
            for inp in inputs if inp.get('name')
        }

        if not has_token:
            if self._submit_without_token(action_url, method, form_data):
                self.vulnerabilities.append({
                    'type': 'CSRF Vulnerability',
                    'url': action_url,
                    'method': method,
                    'has_token': False,
                    'severity': 'High',
                    'description': '폼에 CSRF 토큰이 존재하지 않음',
                    'recommendation': '상태 변경 요청에는 CSRF 토큰을 반드시 포함해야 함'
                })
        else:
            if self._test_token_validation(action_url, method, form_data):
                self.vulnerabilities.append({
                    'type': 'Weak CSRF Protection',
                    'url': action_url,
                    'method': method,
                    'has_token': True,
                    'severity': 'Medium',
                    'description': 'CSRF 토큰이 존재하지만 서버에서 검증되지 않음',
                    'recommendation': 'CSRF 토큰의 서버 측 검증을 강화해야 함'
                })

    def _has_csrf_token(self, form) -> bool:
        """폼 내에 CSRF 토큰 필드 존재 여부 확인"""
        for inp in form.find_all('input'):
            name = inp.get('name', '').lower()
            value = inp.get('value', '')
            if any(token_name in name for token_name in self.csrf_token_names):
                return True
            if inp.get('type', '').lower() == 'hidden' and len(value) > 20:
                if re.match(r'^[A-Za-z0-9+/=_-]{20,}$', value):
                    return True
        return False

    def _submit_without_token(self, url: str, method: str, data: Dict[str, str]) -> bool:
        """CSRF 토큰 없이 요청 시 서버가 거부하지 않는지 테스트"""
        try:
            attacker = requests.Session()
            resp = attacker.request(method, url, data=data,
                                    timeout=self.timeout, allow_redirects=False)
            # 정상 응답이면 취약
            if resp.status_code in [200, 201, 302, 303]:
                return True
        except requests.exceptions.RequestException:
            pass
        return False

    def _test_token_validation(self, url: str, method: str, data: Dict[str, str]) -> bool:
        """잘못된 CSRF 토큰 제출 시에도 통과하는지 테스트"""
        csrf_field = None
        for key in data.keys():
            if any(name in key.lower() for name in self.csrf_token_names):
                csrf_field = key
                break
        if not csrf_field:
            return False

        test_data = data.copy()
        test_data[csrf_field] = 'invalid_token_value_12345'

        try:
            resp = self.session.request(method, url, data=test_data,
                                        timeout=self.timeout, allow_redirects=False)
            if resp.status_code in [200, 201, 302, 303]:
                return True
        except requests.exceptions.RequestException:
            pass
        return False


def test_csrf(target: str, session) -> Dict[str, Any]:
    """
    main.py 에서 호출할 함수
    - target: 진단할 URL
    - session: utils.create_session() 으로 생성한 세션
    반환: {'status', 'description', 'details'}
    """
    scanner = SessionCSRFScanner(session=session)
    try:
        vulns = scanner.scan(target)
        if vulns:
            details = [f"{v['method']} {v['url']} | {v['description']}"
                       for v in vulns]
            return {
                'status': '취약',
                'description': f'CSRF 취약 또는 검증 미흡 {len(vulns)}건 발견',
                'details': details
            }
        else:
            return {
                'status': '양호',
                'description': '모든 폼에서 CSRF 토큰 검증이 적절하게 수행됨',
                'details': []
            }
    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 예외 발생: {str(e)}',
            'details': []
        }
