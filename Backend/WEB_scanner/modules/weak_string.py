# modules/weak_password.py
# -*- coding: utf-8 -*-
"""
약한 문자열(비밀번호) 강도 정책 진단
- 회원가입/비밀번호 변경 페이지의 비밀번호 정책 점검
"""

import re
import requests
from typing import Dict, Any, List


def test_weak_string(target: str, session) -> Dict[str, Any]:
    """
    약한 문자열(비밀번호 강도) 정책 자동 점검
    """
    try:
        response = session.get(target, timeout=10)
        text = response.text.lower()

        # 비밀번호 관련 입력 필드 확인
        if "password" not in text:
            return {
                'status': '인터뷰',
                'description': '비밀번호 입력 필드가 발견되지 않음 (직접 확인 필요)',
                'details': []
            }

        # 패스워드 정책 키워드 확인
        indicators = [
            'minlength', 'maxlength', 'pattern',
            'must contain', 'uppercase', 'lowercase', 'number', 'special'
        ]
        if not any(word in text for word in indicators):
            return {
                'status': '취약',
                'description': '비밀번호 정책(길이/조합 제약)이 페이지 내에서 확인되지 않음',
                'details': ['입력 필드에 minlength, pattern 등의 제약이 없음']
            }

        return {
            'status': '양호',
            'description': '비밀번호 정책이 명시되어 있음 (길이/조합 제약 포함)',
            'details': []
        }

    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 예외 발생: {str(e)}',
            'details': []
        }
