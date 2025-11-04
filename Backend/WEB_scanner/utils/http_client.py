#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# utils/http_client.py - HTTP 요청 처리 (개선판)

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import warnings
from typing import Optional, Tuple, Union, Dict, Any

# 불필요한 urllib3 디테일 로그 억제
logging.getLogger("urllib3").setLevel(logging.WARNING)
# InsecureRequestWarning (verify=False) 만 선택적으로 억제
warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)


def _normalize_timeout(timeout: Optional[Union[int, float, Tuple[int, int]]]) -> Union[int, Tuple[int, int]]:
    """
    timeout을 (connect, read) 튜플 또는 단일 숫자로 정규화하여 반환
    """
    if timeout is None:
        return (5, 15)
    if isinstance(timeout, (int, float)):
        return (int(timeout), int(timeout))
    if isinstance(timeout, tuple) and len(timeout) == 2:
        return (int(timeout[0]), int(timeout[1]))
    # fallback
    return (5, 15)


def create_session(verify: bool = False,
                   timeout: Optional[Union[int, Tuple[int, int]]] = (5, 15),
                   max_retries: int = 2,
                   backoff_factor: float = 0.5,
                   pool_maxsize: int = 10) -> requests.Session:
    """
    HTTP 세션 생성 및 설정

    Args:
        verify: SSL 검증 여부 (운영환경에서는 True 권장)
        timeout: (connect_timeout, read_timeout) 튜플 또는 단일 숫자
        max_retries: 일시적 오류 재시도 횟수
        backoff_factor: 재시도 간격 계산 계수
        pool_maxsize: 커넥션 풀 최대 크기

    Returns:
        requests.Session: 설정된 세션 객체 (추가 속성: session.request_timeout)
    """
    session = requests.Session()
    session.verify = verify

    # 공통 헤더 설정
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    })

    # Retry 정책 설정
    retry = Retry(
        total=max_retries,
        read=max_retries,
        connect=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        # urllib3 버전 따라 인자명이 다를 수 있음(allowed_methods 권장)
        allowed_methods=frozenset(['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'])
    )

    # HTTPAdapter 설정 (pool_maxsize 적용)
    adapter = HTTPAdapter(max_retries=retry, pool_maxsize=pool_maxsize)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    # 기본 타임아웃 저장 (항상 튜플 형식으로 저장)
    session.request_timeout = _normalize_timeout(timeout)

    return session


def safe_request(session: requests.Session,
                 method: str,
                 url: str,
                 return_response: bool = False,
                 timeout: Optional[Union[int, Tuple[int, int]]] = None,
                 **kwargs) -> Union[requests.Response, Dict[str, Any]]:
    """
    안전한 HTTP 요청 래퍼

    Args:
        session: requests.Session 객체
        method: HTTP 메소드 ('GET', 'POST' 등)
        url: 요청 URL
        return_response: True면 requests.Response (raw) 반환 (호출자가 오류/상태 직접 처리)
        timeout: 타임아웃 (단일 숫자 또는 (connect, read)); None이면 session.request_timeout 사용
        **kwargs: requests.request로 전달되는 기타 인자 (params, data, headers 등)

    Returns:
        - return_response=True: requests.Response (성공/실패 모두 반환; 예외는 발생)
        - return_response=False: dict 형태로 결과 요약 반환:
            {'ok': bool, 'status_code': int|None, 'text': str|None, 'error': str|None, 'response': Response|None}
    """
    # normalize timeout
    if timeout is None:
        timeout = getattr(session, 'request_timeout', (5, 15))
    timeout = _normalize_timeout(timeout)

    try:
        # requests.request에서 timeout에 튜플을 넣을 수 있음
        resp = session.request(method, url, timeout=timeout, **kwargs)

        # HTTP 오류 상태(4xx/5xx) 처리
        if 400 <= resp.status_code < 600:
            if return_response:
                # 호출자가 raw response를 보고 싶어함 -> 그대로 반환
                return resp
            return {
                'ok': False,
                'status_code': resp.status_code,
                'text': resp.text[:500] if resp.text is not None else None,
                'error': f'HTTP {resp.status_code}',
                'response': resp
            }

        # 성공(2xx / 3xx)
        if return_response:
            return resp
        return {
            'ok': True,
            'status_code': resp.status_code,
            'text': resp.text,
            'response': resp
        }

    except requests.exceptions.Timeout as e:
        if return_response:
            # 호출자가 raw response 예외 처리를 원하면 예외 그대로 올려줌
            raise
        return {
            'ok': False,
            'status_code': None,
            'text': None,
            'error': 'timeout',
            'detail': str(e),
            'response': None
        }
    except requests.exceptions.ConnectionError as e:
        if return_response:
            raise
        return {
            'ok': False,
            'status_code': None,
            'text': None,
            'error': 'connection_error',
            'detail': str(e),
            'response': None
        }
    except requests.exceptions.RequestException as e:
        if return_response:
            raise
        return {
            'ok': False,
            'status_code': None,
            'text': None,
            'error': 'request_exception',
            'detail': str(e),
            'response': None
        }


# 편의 함수: raw Response 반환 (호출 시 .status_code / .text 사용)
def get(session: requests.Session, url: str, **kwargs) -> requests.Response:
    return safe_request(session, 'GET', url, return_response=True, **kwargs)


def post(session: requests.Session, url: str, **kwargs) -> requests.Response:
    return safe_request(session, 'POST', url, return_response=True, **kwargs)


# 기존 코드와의 호환성을 위한 래퍼
def create_session_legacy() -> requests.Session:
    """
    기존 코드에서 create_session() 호출했을 때의 호환성 제공
    (기존에 timeout=10처럼 단일값을 사용하던 코드에 대응)
    """
    # legacy 기본값을 튜플로 맞춤
    return create_session(verify=False, timeout=(5, 15))
