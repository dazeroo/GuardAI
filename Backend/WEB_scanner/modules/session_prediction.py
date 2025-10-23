#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modules/session_prediction.py - 세션 예측 취약점 검사
"""

import re
import math
from collections import Counter


def calculate_entropy(data):
    """문자열의 엔트로피 계산 (비트 단위)"""
    if not data:
        return 0
    
    length = len(data)
    frequency = Counter(data)
    
    entropy = 0
    for count in frequency.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
    
    # 총 엔트로피 = 문자당 엔트로피 × 길이
    return entropy * length


def analyze_session_pattern(session_ids):
    """세션 ID 패턴 분석"""
    issues = []
    
    if len(session_ids) < 2:
        return ["세션 ID 샘플이 부족합니다 (최소 2개 필요)"]
    
    # 1. 길이 확인
    lengths = [len(sid) for sid in session_ids]
    if min(lengths) < 16:
        issues.append(f"세션 ID 길이가 짧음: {min(lengths)}자 (권장: 32자 이상)")
    
    # 2. 순차적인 패턴 확인
    # 숫자로만 구성된 경우
    if all(sid.isdigit() for sid in session_ids):
        numbers = [int(sid) for sid in session_ids]
        differences = [numbers[i+1] - numbers[i] for i in range(len(numbers)-1)]
        
        # 차이가 일정하면 순차적
        if len(set(differences)) == 1:
            issues.append(f"순차적인 세션 ID (증가량: {differences[0]})")
        elif max(differences) - min(differences) < 10:
            issues.append("거의 순차적인 세션 ID (예측 가능)")
    
    # 3. 엔트로피 계산
    entropies = [calculate_entropy(sid) for sid in session_ids]
    avg_entropy = sum(entropies) / len(entropies)
    
    # 128비트 이상이 권장됨
    if avg_entropy < 80:
        issues.append(f"낮은 엔트로피: {avg_entropy:.1f}비트 (권장: 128비트 이상)")
    
    # 4. 문자 집합 확인
    all_chars = ''.join(session_ids)
    unique_chars = len(set(all_chars))
    
    if unique_chars < 16:
        issues.append(f"제한된 문자 집합 사용: {unique_chars}개 문자만 사용")
    
    # 5. 반복되는 패턴
    for sid in session_ids:
        # 같은 문자가 연속으로 3개 이상
        if re.search(r'(.)\1{2,}', sid):
            issues.append(f"반복되는 문자 패턴 발견: {sid}")
            break
    
    # 6. 타임스탬프 기반 확인
    # Unix timestamp 형태 (10자리 숫자)
    for sid in session_ids:
        timestamp_match = re.search(r'\b\d{10}\b', sid)
        if timestamp_match:
            issues.append("타임스탬프 기반 세션 ID 가능성 (예측 가능)")
            break
    
    return issues


def test_session_prediction(target_url, session):
    """세션 예측 취약점 검사"""
    
    try:
        # 여러 번 요청하여 세션 ID 수집
        session_ids = []
        session_cookie_names = []
        
        # 5번 요청
        for i in range(5):
            # 새로운 세션을 위해 쿠키 초기화
            temp_session = session.__class__()
            temp_session.headers = session.headers.copy()
            temp_session.verify = session.verify
            
            response = temp_session.get(target_url, timeout=10)
            
            # 세션 쿠키 찾기
            session_keywords = [
                'sessionid', 'session_id', 'session', 'sid', 'ssid',
                'phpsessid', 'jsessionid', 'aspsessionid', 'asp.net_sessionid'
            ]
            
            for cookie in response.cookies:
                if any(keyword in cookie.name.lower() for keyword in session_keywords):
                    session_ids.append(cookie.value)
                    if cookie.name not in session_cookie_names:
                        session_cookie_names.append(cookie.name)
        
        if not session_ids:
            return {
                'status': '인터뷰',
                'description': '세션 쿠키가 발견되지 않아 검사할 수 없습니다',
                'details': ['세션을 사용하는 페이지에서 테스트하세요']
            }
        
        # 세션 ID 분석
        vulnerabilities = []
        warnings = []
        
        # 중복 확인
        unique_sessions = set(session_ids)
        if len(unique_sessions) < len(session_ids):
            vulnerabilities.append(
                f"세션 ID가 재사용됨: {len(session_ids)}개 중 {len(unique_sessions)}개만 고유"
            )
        
        # 패턴 분석
        pattern_issues = analyze_session_pattern(list(unique_sessions))
        
        for issue in pattern_issues:
            if any(keyword in issue for keyword in ['순차적', '낮은 엔트로피', '타임스탬프']):
                vulnerabilities.append(issue)
            else:
                warnings.append(issue)
        
        # 세션 ID 예제 표시 (처음 2개만)
        if len(session_ids) >= 2:
            warnings.append(f"수집된 세션 ID 예제:")
            for i, sid in enumerate(session_ids[:2]):
                warnings.append(f"  #{i+1}: {sid}")
        
        # 엔트로피 정보
        if session_ids:
            entropies = [calculate_entropy(sid) for sid in unique_sessions]
            avg_entropy = sum(entropies) / len(entropies)
            warnings.append(f"평균 엔트로피: {avg_entropy:.1f}비트")
        
        # 결과 평가
        if vulnerabilities:
            return {
                'status': '취약',
                'description': '세션 ID가 예측 가능하거나 보안이 약합니다',
                'details': vulnerabilities + warnings
            }
        elif warnings:
            return {
                'status': '인터뷰',
                'description': '세션 ID의 보안 강도를 추가 확인이 필요합니다',
                'details': warnings
            }
        else:
            return {
                'status': '양호',
                'description': '세션 ID가 충분히 무작위적이고 예측 불가능합니다',
                'details': [f'고유한 세션 ID 생성됨', f'평균 엔트로피: {avg_entropy:.1f}비트']
            }
    
    except Exception as e:
        return {
            'status': '인터뷰',
            'description': f'검사 중 오류 발생: {str(e)}',
            'details': []
        }