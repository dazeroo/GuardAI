#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# modules/__init__.py - 취약점 검사 모듈 패키지

from .buffer_overflow import test_buffer_overflow
from .format_string import test_format_string
from .path_traversal import test_path_traversal
from .process_info_leak import test_process_info_leak
from .insufficient_authorization import test_insufficient_authorization
from .weak_password_recovery import test_weak_password_recovery
from .malicious_content import test_malicious_content
from .sql_injection import test_sql_injection
from .xss import test_xss
from .directory_indexing import test_directory_indexing
from .session_timeout import test_session_timeout
from .automation_attack import test_automation_attack
from .csrf import test_csrf
from .ssi_injection import test_ssi_injection
from .ldap_injection import test_ldap_injection
from .xpath_injection import test_xpath_injection
from .file_upload import test_file_upload
from .admin_exposure import test_admin_exposure
from .weak_string import test_weak_string
from .plaintext_transmission import test_plaintext_transmission
from .information_leakage import test_information_leakage
from .location_disclosure import test_location_disclosure
from .session_fixation import test_session_fixation
from .cookie_manipulation import test_cookie_manipulation
from .command_injection import test_command_injection
from .insufficient_authentication import test_insufficient_authentication
from .session_prediction import test_session_prediction

__all__ = [
    'test_buffer_overflow',
    'test_format_string',
    'test_path_traversal',
    'test_process_info_leak',
    'test_insufficient_authorization',
    'test_weak_password_recovery',
    'test_malicious_content',
    'test_sql_injection',
    'test_xss',
    'test_directory_indexing',
    'test_session_timeout',
    'test_automation_attack',
    'test_csrf',
    'test_ssi_injection',
    'test_ldap_injection',
    'test_xpath_injection',
    'test_file_upload',
    'test_admin_exposure',
    'test_weak_string',
    'test_plaintext_transmission',
    'test_information_leakage',
    'test_location_disclosure',
    'test_session_fixation',
    'test_cookie_manipulation',
    'test_command_injection',
    'test_insufficient_authentication',
    'test_session_prediction',
]
