#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 웹 취약점 스캐너 메인 실행 파일

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime

# 모듈 임포트
from modules.buffer_overflow import test_buffer_overflow
from modules.format_string import test_format_string
from modules.ldap_injection import test_ldap_injection
from modules.command_injection import test_command_injection
from modules.sql_injection import test_sql_injection
from modules.ssi_injection import test_ssi_injection
from modules.xpath_injection import test_xpath_injection
from modules.directory_indexing import test_directory_indexing
from modules.information_leakage import test_information_leakage
from modules.malicious_content import test_malicious_content
from modules.xss import test_xss
from modules.weak_string import test_weak_string
from modules.insufficient_authentication import test_insufficient_authentication
from modules.weak_password_recovery import test_weak_password_recovery
from modules.csrf import test_csrf
from modules.session_prediction import test_session_prediction
from modules.insufficient_authorization import test_insufficient_authorization
from modules.session_timeout import test_session_timeout
from modules.session_fixation import test_session_fixation
from modules.automation_attack import test_automation_attack
from modules.process_info_leak import test_process_info_leak
from modules.file_upload import test_file_upload
from modules.file_download import test_file_download
from modules.admin_exposure import test_admin_exposure
from modules.path_traversal import test_path_traversal
from modules.location_disclosure import test_location_disclosure
from modules.plaintext_transmission import test_plaintext_transmission
from modules.cookie_manipulation import test_cookie_manipulation

from utils.http_client import create_session
from utils.report_generator import generate_report, print_banner, generate_html_report, generate_excel_report


def run_scan(target_url, selected_tests=None):
    """모든 취약점 스캔 실행"""
    print_banner(target_url)
    
    # HTTP 세션 생성
    session = create_session()
    
    # 결과 저장
    results = {}
    
    # 전체 테스트 목록 정의
    all_tests = [
        ("1. 버퍼 오버플로우", lambda: test_buffer_overflow(target_url, session)),
        ("2. 포맷스트링", lambda: test_format_string(target_url, session)),
        ("3. LDAP 인젝션", lambda: test_ldap_injection(target_url, session)),
        ("4. 운영체제 명령 실행", lambda: test_command_injection(target_url, session)),
        ("5. SQL 인젝션", lambda: test_sql_injection(target_url, session)),
        ("6. SSI 인젝션", lambda: test_ssi_injection(target_url, session)),
        ("7. XPath 인젝션", lambda: test_xpath_injection(target_url, session)),
        ("8. 디렉터리 인덱싱", lambda: test_directory_indexing(target_url, session)),
        ("9. 정보 누출", lambda: test_information_leakage(target_url, session)),
        ("10. 악성 콘텐츠", lambda: test_malicious_content(target_url, session)),
        ("11. 크로스사이트 스크립팅", lambda: test_xss(target_url, session)),
        ("12. 약한 문자열 강도", lambda: test_weak_string(target_url, session)),
        ("13. 불충분한 인증", lambda: test_insufficient_authentication(target_url, session)),
        ("14. 취약한 패스워드 복구", lambda: test_weak_password_recovery(target_url, session)),
        ("15. 크로스사이트 리퀘스트 변조(CSRF)", lambda: test_csrf(target_url, session)),
        ("16. 세션 예측", lambda: test_session_prediction(target_url, session)),
        ("17. 불충분한 인가", lambda: test_insufficient_authorization(target_url, session)),
        ("18. 불충분한 세션 만료", lambda: test_session_timeout(target_url, session)),
        ("19. 세션 고정", lambda: test_session_fixation(target_url, session)),
        ("20. 자동화 공격", lambda: test_automation_attack(target_url, session)),
        ("21. 프로세스 검증 누락", lambda: test_process_info_leak(target_url, session)),
        ("22. 파일 업로드", lambda: test_file_upload(target_url, session)),
        ("23. 파일 다운로드", lambda: test_file_download(target_url, session)),
        ("24. 관리자 페이지 노출", lambda: test_admin_exposure(target_url, session)),
        ("25. 경로 추적", lambda: test_path_traversal(target_url, session)),
        ("26. 위치 공개", lambda: test_location_disclosure(target_url, session)),
        ("27. 데이터 평문 전송", lambda: test_plaintext_transmission(target_url, session)),
        ("28. 쿠키 변조", lambda: test_cookie_manipulation(target_url, session)),
    ]
    
    # 선택된 테스트만 실행 (선택하지 않으면 전체 실행)
    tests_to_run = all_tests
    if selected_tests:
        tests_to_run = [test for test in all_tests if any(str(num) in test[0] for num in selected_tests)]
    
    # 각 테스트 실행
    for test_name, test_func in tests_to_run:
        print(f"\n[*] {test_name} 검사 중...")
        try:
            result = test_func()
            results[test_name] = result
            
            status = result['status']
            color = '🔴' if status == '취약' else '🟢' if status == '양호' else '🟡'
            print(f"    {color} {status}: {result['description']}")
            
            if result.get('details'):
                for detail in result['details'][:3]:  # 처음 3개만 표시
                    print(f"       - {detail}")
                if len(result['details']) > 3:
                    print(f"       ... 외 {len(result['details']) - 3}개")
                    
        except Exception as e:
            results[test_name] = {
                'status': '인터뷰',
                'description': f'검사 중 오류 발생: {str(e)}',
                'details': []
            }
            print(f"    🟡 인터뷰: 검사 중 오류 발생")
    
    # 리포트 생성
    json_report = generate_report(target_url, results)
    html_report = generate_html_report(target_url, results)
    
    return results, json_report, html_report


def show_menu():
    """테스트 선택 메뉴 표시"""
    print("\n" + "="*70)
    print("검사 항목 선택")
    print("="*70)
    print("  1. 버퍼 오버플로우")
    print("  2. 포맷스트링")
    print("  3. LDAP 인젝션")
    print("  4. 운영체제 명령 실행)")
    print("  5. SQL 인젝션")
    print("  6. SSI 인젝션")
    print("  7. XPath 인젝션")
    print("  8. 디렉터리 인덱싱")
    print("  9. 정보 누출")
    print("  10. 악성 콘텐츠")
    print("  11. 크로스사이트 스크립팅")
    print("  12. 약한 문자열 강도")
    print(" 13. 불충분한 인증")
    print(" 14. 취약한 패스워드 복구")
    print(" 15. 크로스사이트 리퀘스트 변조(CSRF)")
    print(" 16. 세션 예측")
    print(" 17. 불충분한 인가")
    print(" 18. 불충분한 세션 만료")
    print(" 19. 세션 고정")
    print(" 20. 자동화 공격")
    print(" 21. 프로세스 검증 누락")
    print(" 22. 파일 업로드")
    print(" 23. 파일 다운로드")
    print(" 24. 관리자 페이지 노출")
    print(" 26. 위치 공개")
    print(" 27. 데이터 평문 전송")
    print(" 28. 쿠키 변조")
    
    print("\n" + "="*70)
    print("전체 검사: Enter")
    print("선택 검사: 번호 입력 (예: 1,2,5 또는 1-5)")
    print("="*70)


def parse_selection(selection):
    """사용자 선택 파싱"""
    if not selection or selection.strip() == '':
        return None  # 전체 선택
    
    selected = set()
    parts = selection.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            # 범위 (예: 1-5)
            try:
                start, end = map(int, part.split('-'))
                selected.update(range(start, end + 1))
            except:
                pass
        else:
            # 단일 번호
            try:
                selected.add(int(part))
            except:
                pass
    
    return list(selected) if selected else None


def main():
    """메인 함수"""
    print("="*70)
    print(" "*20 + "웹 취약점 자동 진단 스크립트 v2.0")
    print("="*70)
    print("\n[!] 주의: 이 도구는 권한이 있는 시스템에만 사용하세요.")
    print("[!] 무단 스캔은 법적 문제를 일으킬 수 있습니다.\n")
    
    # URL 입력
    target = input("진단할 URL을 입력하세요: ").strip()
    
    if not target:
        print("\n[!] URL을 입력해주세요.")
        return
    
    # URL 형식 검증
    if not target.startswith(('http://', 'https://')):
        target = 'https://' + target
    
    # 검사 항목 선택
    show_menu()
    selection = input("\n선택: ").strip()
    selected_tests = parse_selection(selection)
    
    if selected_tests:
        print(f"\n선택된 항목: {sorted(selected_tests)}")
    else:
        print("\n전체 항목 검사를 시작합니다.")
    
    # 스캔 실행
    try:
        results, json_report, html_report = run_scan(target, selected_tests)
        print(f"\n[+] 스캔 완료!")
        print(f"[+] JSON 리포트: {json_report}")
        print(f"[+] HTML 리포트: {html_report}")
        
    except KeyboardInterrupt:
        print("\n\n[!] 사용자에 의해 스캔이 중단되었습니다.")
    except Exception as e:
        print(f"\n[!] 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
