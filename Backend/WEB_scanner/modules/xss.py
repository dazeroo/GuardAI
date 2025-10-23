# modules/xss.py
# -*- coding: utf-8 -*-
# modules/xss.py

from typing import Dict, Any, List, Optional
import re
import time
from urllib.parse import urljoin, quote_plus

# 기본 페이로드 및 탐지 패턴 (필요시 확장/설정으로 분리 가능)
_DEFAULT_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "<svg onload=alert('XSS')>",
    "<body onload=alert('XSS')>",
    "<input onfocus=alert('XSS') autofocus>",
    "javascript:alert('XSS')",
    "<script>alert(String.fromCharCode(88,83,83))</script>",
    "%3Cscript%3Ealert('XSS')%3C/script%3E",
    "<ScRiPt>alert('XSS')</sCrIpT>",
    "';alert('XSS');//",
]

_DETECTION_PATTERNS = [
    r"<script[^>]*>.*?alert.*?</script>",
    r"<img[^>]*onerror\s*=",
    r"<svg[^>]*onload\s*=",
    r"<body[^>]*onload\s*=",
    r"javascript:\s*alert",
    r"<iframe[^>]*src\s*=\s*['\"]?javascript:",
    r"<details[^>]*ontoggle\s*=",
]


class SessionXSSScanner:
    """Session 기반 XSS 스캐너 (반사형 중심)"""

    def __init__(self,
                 session,
                 timeout: int = 10,
                 payloads: Optional[List[str]] = None,
                 patterns: Optional[List[str]] = None,
                 rate_delay: float = 0.3,
                 max_evidence_len: int = 200):
        """
        session: requests.Session (외부에서 생성해서 전달)
        timeout: 요청 타임아웃 (초)
        payloads: 검사 페이로드 리스트
        patterns: 정규식 기반 탐지 패턴
        rate_delay: 각 요청 사이 대기 초 (부하완화)
        """
        self.session = session
        self.timeout = timeout
        self.payloads = payloads or _DEFAULT_PAYLOADS
        self.patterns = [re.compile(p, re.IGNORECASE) for p in (patterns or _DETECTION_PATTERNS)]
        self.rate_delay = rate_delay
        self.max_evidence_len = max_evidence_len
        self.vulns = []

    def scan_get_params(self, url: str, params: Dict[str, str]) -> List[Dict[str, Any]]:
        """GET 파라미터들에 대해 반사형 XSS 검사"""
        self.vulns = []
        for param in list(params.keys()):
            base_params = params.copy()
            # 기본 페이지를 먼저 가져와서 baseline 확인 (길이/본문)
            try:
                baseline = self.session.get(url, params=base_params, timeout=self.timeout, allow_redirects=True)
                baseline_text = baseline.text or ''
            except Exception:
                baseline_text = ''
            for payload in self.payloads:
                test_params = base_params.copy()
                test_params[param] = payload
                try:
                    resp = self.session.get(url, params=test_params, timeout=self.timeout, allow_redirects=True)
                    text = resp.text or ''
                except Exception as e:
                    # 연결문제 등은 건너뜀(상위에서 처리)
                    continue

                # 정확 일치(원문 반사) 검사
                if payload in text:
                    self.vulns.append(self._make_vuln(
                        vtype='Reflected XSS',
                        url=url,
                        method='GET',
                        parameter=param,
                        payload=payload,
                        evidence=self._extract_evidence(text, payload)
                    ))
                    break  # 해당 파라미터는 취약으로 판단 후 다음 파라미터 검사

                # 패턴 기반 탐지
                for pat in self.patterns:
                    if pat.search(text):
                        self.vulns.append(self._make_vuln(
                            vtype='Reflected XSS (pattern match)',
                            url=url,
                            method='GET',
                            parameter=param,
                            payload=payload,
                            evidence=self._extract_evidence(text, payload) or f'Pattern: {pat.pattern}'
                        ))
                        break
                else:
                    # no pattern match -> continue payload loop
                    time.sleep(self.rate_delay)
                    continue
                # pattern matched -> break payload loop
                break
        return self.vulns

    def scan_post_data(self, url: str, data: Dict[str, str]) -> List[Dict[str, Any]]:
        """POST 데이터에 대해 반사형 XSS 검사"""
        self.vulns = []
        for param in list(data.keys()):
            base_data = data.copy()
            try:
                baseline = self.session.post(url, data=base_data, timeout=self.timeout, allow_redirects=True)
                baseline_text = baseline.text or ''
            except Exception:
                baseline_text = ''
            for payload in self.payloads:
                test_data = base_data.copy()
                test_data[param] = payload
                try:
                    resp = self.session.post(url, data=test_data, timeout=self.timeout, allow_redirects=True)
                    text = resp.text or ''
                except Exception:
                    continue

                if payload in text:
                    self.vulns.append(self._make_vuln(
                        vtype='Reflected XSS',
                        url=url,
                        method='POST',
                        parameter=param,
                        payload=payload,
                        evidence=self._extract_evidence(text, payload)
                    ))
                    break

                for pat in self.patterns:
                    if pat.search(text):
                        self.vulns.append(self._make_vuln(
                            vtype='Reflected XSS (pattern match)',
                            url=url,
                            method='POST',
                            parameter=param,
                            payload=payload,
                            evidence=self._extract_evidence(text, payload) or f'Pattern: {pat.pattern}'
                        ))
                        break
                else:
                    time.sleep(self.rate_delay)
                    continue
                break
        return self.vulns

    def _extract_evidence(self, text: str, payload: str) -> str:
        """증거(페이로드 주변 문맥)를 추출"""
        idx = text.find(payload)
        if idx != -1:
            start = max(0, idx - 100)
            end = min(len(text), idx + len(payload) + 100)
            snippet = text[start:end]
            return snippet[:self.max_evidence_len]
        # 페이로드가 안보이면 패턴 기반 증거를 잘라서 제공
        for pat in self.patterns:
            m = pat.search(text)
            if m:
                start = max(0, m.start() - 50)
                end = min(len(text), m.end() + 50)
                return text[start:end][:self.max_evidence_len]
        return "evidence not found"

    def _make_vuln(self, vtype: str, url: str, method: str, parameter: str, payload: str, evidence: str) -> Dict[str, str]:
        return {
            'type': vtype,
            'url': url,
            'method': method,
            'parameter': parameter,
            'payload': payload,
            'evidence': evidence,
            'severity': 'High'
        }


def test_xss(target: str, session, params: Optional[Dict[str, str]] = None,
             data: Optional[Dict[str, str]] = None, max_checks: int = 10) -> Dict[str, Any]:
    """
    main.py 에서 호출할 어댑터 함수
    - target: 테스트할 URL (절대 URL 권장)
    - session: utils.create_session() 으로 생성한 requests.Session
    - params: GET 파라미터 샘플(없으면 기본 'q' 파라미터를 시도)
    - data: POST 데이터 샘플(폼 기반 사이트 테스트용)
    - max_checks: 파라미터 수가 많을 때 검사 제한(안전장치)
    반환:
      { 'status': '취약'|'양호'|'인터뷰', 'description': str, 'details': [str,...] }
    """
    scanner = SessionXSSScanner(session=session, timeout=10, rate_delay=0.3)
    try:
        # 기본 파라미터 샘플이 없으면 'q' 파라미터로 간단 검사
        if params is None and data is None:
            params = {'q': 'test'}

        vulns = []
        if params:
            # 제한 적용
            p_sample = dict(list(params.items())[:max_checks])
            vulns.extend(scanner.scan_get_params(target, p_sample))

        if data:
            d_sample = dict(list(data.items())[:max_checks])
            vulns.extend(scanner.scan_post_data(target, d_sample))

        if vulns:
            details = []
            for v in vulns:
                details.append(f"{v.get('method')} param={v.get('parameter')} payload={v.get('payload')[:80]} evidence={v.get('evidence')[:120]}")
            return {
                'status': '취약',
                'description': f'XSS 의심 {len(vulns)}건 발견',
                'details': details
            }
        else:
            return {
                'status': '양호',
                'description': '반사형 XSS 징후 미검출',
                'details': []
            }
    except Exception as e:
        # 상세 에러는 디버그 모드에서만 보여주는 편이 안전
        return {
            'status': '인터뷰',
            'description': f'검사 중 예외 발생: {str(e)}',
            'details': []
        }
