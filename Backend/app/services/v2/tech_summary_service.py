import pandas as pd
import re, io
from typing import List, Dict, Optional

DB_CODE_MAP = {
    "D-01": {"name": "기본 계정의 패스워드, 권한 등을 변경하여 사용", "result": "[인터뷰]\nOS 인증('auth_socket')을 사용하는 현재 방식이 내부 보안 정책 및 가이드라인(D-01)을 준수하는 것으로 협의되었는지, 'root' 계정으로 원격 접속(localhost 외)이 허용되어 있는지, 허용된 경우 해당 계정의 인증 방식(plugin)이 무엇인지 담당자 확인이 필요합니다.", "countermeasure": "주요정보통신기반시설 가이드를 참고하시어, 패스워드 관리 기준을 준수하도록 기본(관리자) 계정의 디폴트 패스워드 및 권한 정책을 변경해주시기 바랍니다.", "interview":"[인터뷰]\n해당 항목 관련 MySQL 기능이나 플러그인이 존재하는지 담당자 확인이 필요합니다."},
    "D-02": {"name": "데이터베이스의 불필요 계정을 제거하거나, 잠금설정 후 사용", "result": "[인터뷰]\n활성화된 계정 중 guardai('%'), seung('%'), book('localhost') 계정이 현재 실제 사용 중인 계정이 맞는지, 해당 계정들의 용도가 무엇인지 담당자 확인이 필요합니다.", "countermeasure": "주요정보통신기반시설 가이드를 참고하시어, 계정별 용도를 파악한 후 불필요한 계정을 삭제하여 주시기 바랍니다.", "interview":"[인터뷰]\n인가되지 않은 계정, 퇴직자 계정, 테스트 계정 등 불필요한 계정이 존재하는지 담당자 확인이 필요합니다."},
    "D-03": {"name": "패스워드의 사용기간 및 복잡도를 기관 정책에 맞도록 설정", "result": "[대응 방안]\n주요정보통신기반시설 가이드를 참고하시어, validate_password 컴포넌트를 설치(INSTALL COMPONENT)하고 관련 정책 변수(예: validate_password.length, validate_password.policy)를 설정하여 패스워드 복잡도 검증 기능을 활성화해주시기 바랍니다. 또한, default_password_lifetime 값을 90(일) 이상으로 설정하여 패스워드 만료 기간이 적용되도록 글로벌 변수 및 my.cnf 설정 파일에 반영해주시기 바랍니다.", "countermeasure": "[대응 방안]\n주요정보통신기반시설 가이드를 참고하시어, 내부 규정에 맞게 패스워드 사용기간 및 복잡도 설정을 적용해주시기 바랍니다."},
    "D-04": {"name": "데이터베이스 관리자 권한을 꼭 필요한 계정 및 그룹에 허용", "result": "[인터뷰]\nguardai와 seung 계정이 실제 관리 업무(DBA)를 수행하는 계정이 맞는지, 관리자 권한이 업무상 반드시 필요한지, 해당 계정들의 접속을 '%'가 아닌 특정 IP나 localhost로 제한할 수 있는지 담당자 확인이 필요합니다.", "countermeasure": "주요정보통신기반시설 가이드를 참고하시어, 관리자 권한이 필요한 계정 및 그룹에만 관리자 권한 부여해주시기 바랍니다.", "interview":"[인터뷰]\n관리자 권한이 필요 없는 계정 및 그룹에 권한이 부여되었는지 담당자 확인이 필요합니다."},
    "D-05": {"name": "원격에서 DB 서버로의 접속 제한", "result": "[대응 방안]\nguardai 및 seung 계정의 사용 용도를 검토한 후, 주요정보통신기반시설 가이드를 참고하시어 원격 접속이 불필요한 경우 host 설정을 'localhost'로 변경해주시기 바랍니다. 만약 원격 접속이 반드시 필요하다면, '%' 대신 실제 접속이 필요한 애플리케이션 서버의 IP 주소나 IP 대역으로 명시적으로 제한하여 RENAME USER 또는 ALTER USER를 통해 접근 제어를 강화해주시기 바랍니다.","countermeasure": "주요정보통신기반시설 가이드를 참고하시어, DB서버에 대해 지정된 IP주소에서만 접근 가능하도록 설정해주시기 바랍니다.", "interview":"[인터뷰]\n현재 지정되어 있는 IP주소에서 DB 서버 접근 권한이 필요한지 담당자 확인이 필요합니다."},
    "D-06": {"name": "DBA 이외의 인가되지 않은 사용자 시스템 테이블에 접근할 수 없도록 설정", "countermeasure": "주요정보통신기반시설 가이드를 참고하시어, 시스템 테이블 및 데이터 딕셔너리에 대한 접근 권한을 최소화하고, DBA 및 필수 역할에만 접근을 허용해주시기 바랍니다."},
    "D-07": {"name": "오라클 데이터베이스의 경우 리스너의 패스워드를 설정하여 사용", "countermeasure": "주요정보통신기반시설 가이드를 참고하시어, Oracle Listener 패스워드를 설정해주시기 바랍니다.", "interview":"해당 항목 관련 MySQL 기능이나 플러그인이 존재하는지 담당자 확인이 필요합니다."},
    "D-08": {"name": "응용프로그램 또는 DBA 계정의 Role이 Public으로 설정되지 않도록 조정", "countermeasure": "주요정보통신기반시설 가이드를 참고하시어, PUBLIC 롤에 부여된 불필요한 권한을 회수하고, 각 계정에는 최소한의 필수 권한만 부여해주시기 바랍니다.", "interview": "해당 항목 관련 MySQL 기능이나 플러그인이 존재하는지 담당자 확인이 필요합니다."},
    "D-09": {"name": "OS_ROLES, REMOTE_OS_AUTHENTICATION, REMOTE_OS_ROLES를 FALSE로 설정", "result": "[인터뷰]\nPAM 플러그인을 사용하지 않는 것은 확인되었으나, D-04 항목에서 식별된 관리자 계정(guardai, seung 등)이 특정 개인에게 할당된 계정인지, 혹은 여러 담당자가 공유하여 사용하는 '공용 계정'인지 담당자 확인이 필요합니다.", "countermeasure": "주요정보통신기반시설 가이드를 참고하시어, 데이터베이스 파라미터 파일에서 해당 값들을 FALSE로 설정하여 운영체제 인증을 비활성화하고 데이터베이스 자체 인증을 사용해주시기 바랍니다.", "interview":"[인터뷰]\n해당 항목 관련 MySQL 기능이나 플러그인이 존재하는지 담당자 확인이 필요합니다."},
    "D-10": {"name": "데이터베이스에 대해 최신 보안패치와 밴더 권고사항을 모두 적용", "result": "[대응 방안]\n현재 8.0.42 버전에서 발견된 보안 취약점(예: CVE-2025-53023 등)을 해결하기 위해, 벤더 권고 사항을 검토하고 서비스 영향도를 평가한 후 최신 안정화 버전(현재 8.0.44)으로 보안 패치를 적용해주시기 바랍니다. 또한, 운영체제(Ubuntu)의 패키지 매니저(apt)를 통해 mysql-server 패키지를 정기적으로 업데이트하여 보안 패치가 누락되지 않도록 관리해주시기 바랍니다.", "countermeasure": "[대응 방안]\n주요정보통신기반시설 가이드를 참고하시어, 정기적으로 데이터베이스 벤더가 제공하는 보안 패치 및 업데이트를 확인하고 신속하게 적용해주시기 바랍니다."},
    "D-11": {"name": "데이터베이스의 접근, 변경, 삭제 등의 감사기록이 기관의 감사기록 정책에 적합하도록 설정", "result": "[대응 방안]\n주요정보통신기반시설 가이드를 참고하시어, 데이터베이스 감사 플러그인(MySQL Enterprise Audit 또는 오픈소스 감사 플러그인)을 설치 및 활성화해야 합니다. 플러그인 설치 후, 감사 정책에 맞게 audit_log_policy (기록할 이벤트 유형), audit_log_format (로그 형식), audit_log_rotate_on_size (로그 로테이션) 등의 관련 변수를 설정하여 로그인 실패, DDL, DML 등의 행위가 기록되도록 조치해주시기 바랍니다.", "countermeasure": "[대응 방안]\n주요정보통신기반시설 가이드를 참고하시어, 로그인 시도, DDL/DML 작업 등 주요 활동에 대한 감사를 활성화하고, 감사 로그를 정기적으로 검토 및 보관해주시기 바랍니다."},
    "D-12": {"name": "패스워드 재사용에 대한 제약 설정", "result": "[대응 방안]\n주요정보통신기반시설 가이드를 참고하시어, password_history 값을 기관의 정책(권고값: 5 이상)에 맞게 설정해주시기 바랍니다. 이 설정은 D-03 항목에서 언급된 validate_password 컴포넌트가 활성화되어야 적용되므로, 해당 컴포넌트 설치 및 활성화 조치 후 my.cnf 파일과 글로벌 변수에 함께 반영해주시기 바랍니다.", "countermeasure": "주요정보통신기반시설 가이드를 참고하시어, 데이터베이스의 패스워드 정책을 통해 사용자가 이전에 사용했던 패스워드를 일정 기간 재사용할 수 없도록 제한해주시기 바랍니다.", "interview":"[인터뷰]\n해당 항목 관련 MySQL 기능이나 플러그인이 존재하는지 담당자 확인이 필요합니다."},
    "D-13": {"name": "DB 사용자 계정을 개별적으로 부여하여 사용", "result": "[인터뷰]\n식별된 계정(guardai, seung, book)들이 특정 담당자 개인에게 1:1로 부여된 계정이 맞는지, 혹은 팀이나 여러 담당자가 패스워드를 공유하며 사용하는 공용 계정인지 담당자 확인이 필요합니다.", "countermeasure": "주요정보통신기반시설 가이드를 참고하시어, 공용 계정 사용을 금지하고, 모든 사용자에게 개인별 계정을 발급하여 책임 추적성을 확보해주시기 바랍니다.", "interview":"[인터뷰]\n현재 불필요한 계정이 존재하는지, 공용 계정을 사용하고 있는지 담당자 확인이 필요합니다."},
    "D-14": {"name": "불필요한 ODBC/OLE-DB 데이터 소스와 드라이브를 제거하여 사용", "result": "[인터뷰]\n사용자 DSN 탭에 등록된 'Excel Files'와 'MS Access Database'가 현재 서버 운영 및 업무에 반드시 필요한 데이터 원본(DSN)인지, 드라이버 탭에 설치된 'Microsoft Access Driver' 및 'Microsoft Excel Driver'가 데이터베이스 서버 운영에 필수적인지 담당자 확인이 필요합니다.", "countermeasure": "주요정보통신기반시설 가이드를 참고하시어, 시스템에 설치된 데이터 소스 및 드라이버를 검토하고, 사용하지 않는 항목은 삭제해주시기 바랍니다.", "interview":"[인터뷰]\n불필요한 ODBC/OLE-DB가 존재하는지 담당자 확인이 필요합니다."},
    "D-15": {"name": "일정 횟수의 로그인 실패 시 이에 대한 잠금정책이 설정", "result": "[대응 방안]\nD-03 항목의 대응방안과 연계하여, validate_password 컴포넌트를 설치 및 활성화해주시기 바랍니다. 이후, my.cnf 설정 파일 및 글로벌 변수에 failed_login_attempts (권고값: 5 이하) 및 password_lock_time (권고값: 1 이상, 단위: 일) 값을 설정하여 로그인 실패 시 계정 잠금 정책이 적용되도록 조치해주시기 바랍니다.", "countermeasure": "주요정보통신기반시설 가이드를 참고하시어, 지정된 횟수 이상 로그인에 실패한 계정은 일정 시간 동안 자동으로 잠기도록 데이터베이스 보안 정책을 설정해주시기 바랍니다.","interview":"[인터뷰]\n해당 항목 관련 MySQL 기능이나 플러그인이 존재하는지 담당자 확인이 필요합니다."},
    "D-16": {"name": "데이터베이스의 주요 파일 보호 등을 위해 DB 계정의 umask를 022 이상으로 설정하여 사용", "countermeasure": "주요정보통신기반시설 가이드를 참고하시어, 데이터베이스 소프트웨어 소유자 계정의 umask 값을 022 이상으로 설정해주시기 바랍니다.", "interview": "Unix OS를 사용하고 있는지 담당자 확인이 필요합니다."},
    "D-17": {"name": "데이터베이스의 주요 설정파일, 패스워드 파일 등과 같은 주요 파일들의 접근 권한이 적절하게 설정", "result": "[대응 방안]\n데이터 디렉터리(/var/lib/mysql)의 권한(700)은 양호하므로 현행 유지를 권고합니다. 다만, 설정 파일의 실제 대상인 /etc/alternatives/my.cnf 파일의 권한을 644 (소유자 rw, 그룹 r, other r) 또는 640 (소유자 rw, 그룹 r, other -)으로 변경하고 소유자를 root:root (또는 root:mysql)로 설정하여 비인가자의 수정을 방지해주시기 바랍니다.", "countermeasure": "[대응 방안]\n주요정보통신기반시설 가이드를 참고하시어, 데이터베이스 관련 중요 파일들의 소유자와 권한을 주기적으로 점검하고, 인가된 관리자 외에는 접근할 수 없도록 제한해주시기 바랍니다."},
    "D-18": {"name": "관리자 이외의 사용자가 오라클 리스너의 접속을 통해 리스너 로그 및 trace 파일에 대한 변경 제한", "result": "[대응 방안]\nguardai와 seung 계정이 SYSTEM_VARIABLES_ADMIN 권한(글로벌 변수 변경)이 업무상 반드시 필요한 계정이 맞는지, debian-sys-main 계정이 OS 관리 스크립트 등에 의해 해당 권한을 정상적으로 사용하는 것이 맞는지 담당자 확인이 필요합니다.", "countermeasure": "주요정보통신기반시설 가이드를 참고하시어, 리스너 로그 및 트레이스 파일의 권한을 관리자만 쓸 수 있도록 설정하고, 리스너의 원격 관리 기능을 비활성화해주시기 바랍니다.", "interview":"[인터뷰]\n해당 항목 관련 MySQL 기능이나 플러그인이 존재하는지 담당자 확인이 필요합니다."},
    "D-19": {"name": "패스워드 확인함수가 설정되어 적용", "result": "[대응 방안]\n주요정보통신기반시설 가이드를 참고하시어 INSTALL COMPONENT 'file://validate_password'; 명령을 실행하여 패스워드 검증 컴포넌트를 설치 및 활성화해주시기 바랍니다. 이후, my.cnf 설정 파일과 글로벌 변수에 validate_password.policy (권고값: STRONG 또는 2), validate_password.length (권고값: 8 이상) 등 관련 정책 변수를 설정하여 패스워드 복잡도 검증 기능이 적용되도록 조치해주시기 바랍니다.", "countermeasure": "주요정보통신기반시설 가이드를 참고하시어, 데이터베이스에서 제공하는 패스워드 복잡도 검증 함수를 활성화하여 사용자가 정책에 맞는 강력한 패스워드를 설정하도록 하시기 바랍니다.", "interview":"[인터뷰]\n해당 항목 관련 MySQL 기능이나 플러그인이 존재하는지 담당자 확인이 필요합니다."},
    "D-20": {"name": "인가되지 않은 Object Owner의 제한", "result": "[인터뷰]\n'book' 계정(애플리케이션 계정으로 추정)이 'wordpress' DB에 대해 객체 생성(CREATE) 및 뷰 생성(CREATE VIEW) 권한이 반드시 필요한지 담당자 확인이 필요합니다. (일반적으로 웹 애플리케이션 계정은 DML 권한만 필요합니다.)", "countermeasure": "주요정보통신기반시설 가이드를 참고하시어, 데이터베이스 객체는 반드시 정해진 소유자(스키마) 하에 생성되도록 관리하고, 불필요한 계정이 객체를 소유하지 않도록 통제하시기 바랍니다.", "interview":"해당 항목 관련 MySQL 기능이나 플러그인이 존재하는지 담당자 확인이 필요합니다."},
    "D-21": {"name": "인가되지 않은 GRANT OPTION 사용 제한", "result": "[인터뷰]\n'seung' 계정이 다른 사용자에게 권한을 부여하는 관리(DBA) 업무를 수행하는 것이 맞는지, GRANT OPTION이 업무상 반드시 필요한지 담당자 확인이 필요합니다.", "countermeasure": "주요정보통신기반시설 가이드를 참고하시어, WITH GRANT OPTION을 사용하여 권한을 부여하는 것을 최소화하고, 꼭 필요한 경우에만 제한적으로 사용하여 권한 남용을 방지하시기 바랍니다.", "interview":"[인터뷰]\nWITH_GRANT_OPTION이 ROLE에 의하여 설정되어있는지 담당자 확인이 필요합니다."},
    "D-22": {"name": "데이터베이스의 자원 제한 기능을 TRUE로 설정", "result": "[대응 방안]\n특정 계정의 비정상적인 쿼리나 접속 폭주로 인한 서비스 장애를 방지하기 위해 각 계정(guardai, seung, book 등)의 용도와 서비스 부하를 분석하여, ALTER USER ... WITH MAX_QUESTIONS N MAX_UPDATES N MAX_CONNECTIONS N 명령을 통해 시스템 자원을 고갈시키지 않도록 적절한 임계값을 설정해주시기 바랍니다.", "countermeasure": "[대응 방안]\n주요정보통신기반시설 가이드를 참고하시어, RESOURCE_LIMIT 파라미터를 TRUE로 설정하고 프로파일을 통해 사용자별 자원 사용량을 제한하여 서비스 거부 공격 등을 방지해주시기 바랍니다.", "interview":"[인터뷰]\n해당 항목 관련 MySQL 기능이나 플러그인이 존재하는지 담당자 확인이 필요합니다."},
    "D-23": {"name": "보안에 취약하지 않은 버전의 데이터베이스를 사용", "result": "[대응 방안]\nD-10 항목의 대응방안과 동일하게, 현재 버전에 존재하는 보안 취약점을 해결하기 위해 벤더 권고 사항을 검토하고 서비스 영향도를 평가한 후, 최신 안정화 버전(현재 8.0.44)으로 보안 패치를 적용하여 주시기 바랍니다.", "countermeasure": "[대응 방안]\n주요정보통신기반시설 가이드를 참고하시어, 벤더의 지원이 종료된(EOL) 버전 사용을 중단하고, 안정성과 보안이 검증된 최신 버전의 데이터베이스로 업그레이드해주시기 바랍니다."},
    "D-24": {"name": "Audit Table은 데이터베이스 관리자 계정에 접근하도록 제한", "result": "[대응 방안]\n향후 D-11의 조치에 따라 감사 기능을 활성화하고 로그 저장 방식을 'TABLE'로 설정할 경우(예: audit_log_handler=TABLE), 감사 로그가 저장되는 mysql.audit_log 테이블에 대해 관리자 계정을 제외한 모든 일반 사용자의 SELECT, UPDATE, DELETE 권한을 REVOKE 하여 접근을 제한해주시기 바랍니다.", "countermeasure": "주요정보통신기반시설 가이드를 참고하시어, 감사 테이블에 대한 접근 권한을 DBA 역할이나 감사 관리자에게만 부여하고, 일반 사용자의 접근은 제한해주시기 바랍니다.", "interview":"[인터뷰]\n해당 항목 관련 MySQL 기능이나 플러그인이 존재하는지 담당자 확인이 필요합니다."},
}

WEB_CODE_MAP: Dict[str, dict] = {
    "BO": {"name": "버퍼 오버플로우", "result": "[대응 방안]\n주요정보통신기반시설 가이드를 참고하시어 파라미터의 입력 값 범위를 제한하시고, 허용 범위를 벗어나는 경우 에러 페이지가 반환되지 않도록 설정하여 주시기 바랍니다.", "countermeasure": "[대응 방안]\n파라미터 값을 외부에서 입력받아 사용하는 경우 입력 값 범위를 제한하며, 허용 범위를 벗어나는 경우 에러 페이지가 반환되지 않도록 조치하여 주시기 바랍니다."},
    "FS": {"name": "포맷스트링", "countermeasure": "[대응 방안]\n웹 서버 프로그램을 최신 버전으로 업데이트하고 포맷 스트링 버그를 발생시키는 문자열에 대한 검증 로직을 구현하여 주시기 바랍니다."},
    "LI": {"name": "LDAP 인젝션", "countermeasure": "[대응 방안]\n영문(a-z, A-Z)과 숫자(0-9)만 입력을 허용하고, 특수문자에 대해서는 실행 명령이 아닌 일반문자로 인식되도록 필터링 처리하여 주시기바랍니다. 또한 임의의 LDAP 쿼리 입력에 대한 검증 로직을 구현하여 주시기 바랍니다."},
    "OC": {"name": "운영체제 명령 실행", "countermeasure": "[대응 방안]\n취약한 버전의 웹 서버 및 웹 애플리케이션 서버는 최신 버전으로 업데이트를 적용하여 주시고, 입력 값에 대한 파라미터 데이터의 '&', '|', ';', '`' 문자에 대해서는 필터링 처리하여 주시기 바랍니다.", "interview":"[인터뷰]\nURL에 파라미터가 없어 자동 진단이 불가능합니다. GET 파라미터를 포함한 URL로 다시 진단하여 주시기 바랍니다."},
    "SI": {"name": "SQL 인젝션", "countermeasure": "[대응 방안]\nSQL 쿼리에 사용되는 문자열의 유효성을 검증하는 로직을 구현하여 주시고 시스템에서 제공하는 에러 메시지 및 DBMS에서 제공하는 에러 코드가 노출되지 않도록 예외처리해주시기 바랍니다." , "interview":"URL에 파라미터가 없어 자동 진단이 불가능합니다. GET 파라미터를 포함한 URL로 다시 진단하여 주시기 바랍니다."},
    "SS": {"name": "SSI 인젝션", "countermeasure": "[대응 방안]\n웹 서버에서 SSI를 비활성화하거나, 입력이 가능한 문자열을 제한하여 주시고 그 외의 문제들에 대해서는 필터링 처리하여 주시기바랍니다.", "interview":"URL에 파라미터가 없어 자동 진단이 불가능합니다. GET 파라미터를 포함한 URL로 다시 진단하여 주시기 바랍니다."},
    "XI": {"name": "XPath 인젝션", "countermeasure": "[대응 방안]\n허용된 문자 이외의 모든 입력을 허용하지 않아야 하며, XPath 쿼리에 사용자가 값을 입력할 수 있는 경우, 엄격한 입력 값 검증을 통해 필요 문자만을 받아들이게 로직을 구현하여 주시기 바랍니다.", "interview": "실제 파라미터가 존재하지 않아, 기본 파라미터(q)로 테스트되었지만, 파라미터가 포함된 URL로 다시 진단하여 주시기 바랍니다."},
    "DI": {"name": "디렉터리 인덱싱", "result": "[대응 방안]\n주요정보통신기반시설 가이드를 참고하시어 Apache 웹 서버 설정 파일(httpd.conf 또는 apache2.conf 또는 VirtualHost 설정)에서 해당 디렉터리 또는 전체 웹 루트에 설정된 Options의  Indexes 옵션을 제거하여 주시기 바랍니다.", "countermeasure": "[대응 방안]\nApache 웹 서버 설정 파일 'httpd.conf' 내 Options의  Indexes 옵션을 제거하여 주시기 바랍니다. 또한 'AllowOverride None','Deny from all'로 설정하여 %3f.jsp 문자를 필터링하여 주시기 바랍니다."},
    "IL": {"name": "정보 누출", "result":"주요정보통신기반시설 가이드를 참고하시어 httpd.conf 또는 apache2.conf 설정파일에서 'ServerTokens Prod'로 설정 값을 변경하여 주시고 'ServerSignature Off'로 설정 값을 변경하여 주시기 바랍니다.", "countermeasure": "[대응 방안]\nhttpd.conf 또는 apache2.conf 설정파일에서 'ServerTokens Prod','ServerSignature Off'로 설정 값을 변경하여 주시고 에러 코드에 대해 별도의 에러 페이지로 Redirect 하도록 설정하여 주시기 바랍니다."},
    "CS": {"name": "악성 콘텐츠", "countermeasure": "[대응 방안]\n악성코드가 포함될 수 있는 콘텐츠를 삽입 또는 업로드하지 못하게 필터링을 적용하여 주시기 바랍니다."},
    "XS": {"name": "크로스사이트 스크립팅", "countermeasure": "[대응 방안]\n사용자 입력 값에 대해 특수문자, 특수 구문 필터링 로직을 trim, replace 함수를 사용해 구현하여 주시고, 스크립트 실행을 방지하는 검증 로직을 구현하여 주시기 바랍니다"},
    "BF": {"name": "약한 문자열 강도", "result": "[대응 방안]\n주요정보통신기반시설 가이드를 참고하시어 무차별 대입 공격을 방어할 수 있도록 Server Side Script(PHP, ASP, JSP 등)를 활용해 로그인 인증 실패 횟수를 3~5회 이상 초과 시 해당 계정의 접근을 제한하시기 바랍니다.", "countermeasure": "[대응 방안]\n취약한 계정 및 패스워드를 삭제하고, 사용자가 취약한 계정이나 패스워드를 등록하지 못하도록 패스워드 규정이 반영된 체크 로직을 회원가입, 정보변경, 패스워드 변경 등 적용 필요한 페이지에 모두 구현하여 주시기 바랍니다", "interview":"진단 중 예외가 발생하여 담당자 확인이 필요합니다."},
    "IA": {"name": "불충분한 인증", "result": "[대응 방안]\n주요정보통신기반시설 가이드를 참고하시어 접근 제어가 필요한 모든 페이지(예: 중요정보페이지, 마이페이지)에 접근 시, Server Side Script(PHP, ASP, JSP 등)를 활용해 본인 인증을 재확인하는 로직을 구현하여 주시기 바랍니다.", "countermeasure": "[대응 방안]\n중요정보를 표시하는 페이지에서는 본인 인증을 재확인 하는 로직을 구현하여 주시고, 사용자가 인증 후 이용 가능한 페이지에 접근할 때마다 승인을 얻는 사용자인지 페이지마다 검증하여 주시기 바랍니다.", "interview":"본인 인증을 재확인 하는 로직을 발견하지 못하여 담당자 확인이 필요합니다."},
    "PR": {"name": "취약한 패스워드 복구", "result":"주요정보통신기반시설 가이드를 참고하시어 패스워드 복구 시, 임시패스워드를 발급받고 임시 패스워드를 발급받은 즉시 새로운 패스워드로 재설정하도록 설정 하시고, 난수를 사용해 패스워드를 재설정하도록 설정하여 주시기 바랍니다.", "countermeasure": "[대응 방안]\n패스워드 재발급 검증 실패에 대한 임계값을 설정하여 주시고, 검증 후 임시패스워드를 발급하도록 설계하여 주시기 바랍니다. 또한 인증된 사용자 메일이나 SMS에서만 재설정된 패스워드를 확인할 수 있도록 조치하여 주시기 바랍니다.", "interview":"비밀번호 재설정 기본 검사는 통과하였지만, 난수성 및 이메일/SMS 전송 여부는 담당자 확인이 필요합니다."},
    "CF": {"name": "크로스사이트 리퀘스트 변조", "countermeasure": "[대응 방안]\n주요 요청에 대해 사용자의 재인증을 요구하고, HTTP 헤더의 Referer 검증 로직을 구현하여 주시기 바랍니다. 또한 정상적인 요청과 비정상적인 요청을 구분할 수 있도록 Hidden Form을 사용하여 임의의 암호화된 토큰(세션 ID, Timestamp, nonce 등)을 추가하고 이 토큰을 검증하도록 설계하여 주시기 바랍니다."},
    "SE": {"name": "세션 예측", "countermeasure": "[대응 방안]\n예측 불가능한 복잡하고 긴 세션 ID를 생성하기 위해 암호학적으로 안전한 난수 생성기를 사용하여 주시고, 세션 ID는 로그인 시마다 추측할 수 없는 새로운 세션 ID로 발급되는 로직을 구현하여 주시기 바랍니다.", "interview": "세션 쿠키가 발견되지 않아 자동 진단이 불가능합니다. 세션을 사용하는 URL로 다시 진단하여 주시기 바랍니다."},
    "IN": {"name": "불충분한 인가", "countermeasure": "[대응 방안]\n접근 제어가 필요한 중요 페이지는 통제수단을 구현하여 인가된 사용자 여부를 검증 후 해당 페이지에 접근할 수 있도록 로직을 구현하여 주시고, 페이지별 권한 매트릭스를 작성하여 접근제어가 필요한 모든 페이지에서 권한 체크가 이뤄지도록 구현하여 주시기 바랍니다.", "interview": "다음 주소에 대한 담당자 확인이 필요합니다. 'http://192.168.0.63/wordpress/admin : anon=404, auth=404', 'http://192.168.0.63/wordpress/api/admin/data : anon=404, auth=404', 'http://192.168.0.63/wordpress/user/profile : anon=404, auth=404'"},
    "SC": {"name": "불충분한 세션 만료", "result":"주요정보통신기반시설 가이드를 참고하시어 세션 타임아웃을 10분으로 설정하여 주시기 바랍니다.", "countermeasure": "[대응 방안]\nphp.ini 파일에서 ini_set() 함수를 사용하여 세션 타임아웃을 10분으로 설정하여 주시기 바랍니다. ", "interview":"세션 만료 검사 중 오류가 발생하여 담당자 확인이 필요합니다."},
    "SF": {"name": "세션 고정", "countermeasure": "[대응 방안]\n로그인할 때마다 기존 세션 ID는 파기하고 예측 불가능한 새로운 세션 ID를 발급받도록 로직을 구현하여 주시기 바랍니다.", "interview": "세션 쿠키가 발견되지 않아 자동 진단이 불가능합니다. 세션을 사용하는 URL로 다시 진단하여 주시기 바랍니다."},
    "AU": {"name": "자동화 공격", "result": "[대응 방안]\n주요정보통신기반시설 가이드를 참고하시어 캡차(CAPTCHA)를 활용하여 반복적인 로그인 시도에 대한 일회성 확인 로직을 구현하여주시고, 자동화 공격을 감지하고 방어할 수 있는 IDS/IPS 시스템을 구축하여 주시기 바랍니다.", "countermeasure": "[대응 방안]\n로그인시도, 게시글 등록 등에 대한 사용자 요청이 일회성이 될 수 있도록 CAPTCHA를 도입하고, 자동화 공격을 감지하고 방어할 수 있는 IDS/IPS 시스템을 구축하여 주시기 바랍니다."},
    "PV": {"name": "프로세스 검증 누락", "countermeasure": "[대응 방안]\n페이지별 권한 매트릭스를 작성하여 전 페이지에서 권한 체크가 이뤄지도록 구현하여 주시고, 인증이 필요한 모든 페이지에 대해 유효 세션임을 확인하는 프로세스 미치 접근 요청자의 권한 검증 로직을 적용하여 주시기 바랍니다.", "interview":"접근 요청에 실패하여 담당자 확인이 필요합니다."},
    "FU": {"name": "파일 업로드", "countermeasure": "[대응 방안]\nApache 설정 파일인 httpd.conf Directory 섹션의 AllowOverride을 FileInfo 또는 All로 설정하여 업로드 파일의 확장자 및 타입을 제한하여 허용된 확장자만 업로드 가능하도록 설정하여 주시고, 업로드 파일을 위한 전용 디렉터리를 별도로 생성한 뒤 실행 설정을 제거하여 Server Side Script가 업로드되더라도 실행되지 않는 환경을 구축하여 주시기 바랍니다."},
    "FD": {"name": "파일 다운로드", "countermeasure": "[대응 방안]\n php.ini 에서 magic_quotes_gpc를 On으로 설정하여 '.\./' 와 같은 문자열 입력 시 치환되도록 설정하여 주시기 바랍니다.", "interview":"URL에 파라미터가 없어 자동 진단이능합니다. file, download, path, doc 등의 파라미터를 포함한 URL로 다시 진단하여 주시기 바랍니다."},
    "AE": {"name": "관리자 페이지 노출", "countermeasure": "[대응 방안]\n관리자 페이지 URL을 추측하기 어렵게 변경하고, 지정된 IP만 관리자 페이지에 접근할 수 있도록 제한하여 주시기 바랍니다. 단, 부득이하게 관리자 페이지를 외부에 노출해야 하는 경우 관리자 페이지 로그인 시 2차 인증(otp, vpn, 인증서 등) 적용하여 주시기 바랍니다.", "interview":"관리자/로그인 페이지 1개 발견되어 담당자 확인이 필요합니다. [포트 체크] 포트 노출된 관리자 페이지 추정: http://192.168.0.63:80/ (상태코드 200)"},
    "PT": {"name": "경로 추적", "countermeasure": "[대응 방안]\n사용자가 임의로 접근할 수 있는 최상위 디렉터리를 웹 루트 디렉터리로 설정하여 웹 서버의 시스템 루트 디렉터리로 접근하지 못하게 제한하여 주시고 웹 사이트에서 접근하려는 파일이 있는 디렉터리에 chroot 환경을 적용하여 경로 추적 공격을 최소화하여 주시기 바랍니다."},
    "PL": {"name": "위치 공개", "result": "[대응 방안]\n주요정보통신기반시설 가이드를 참고하시어 캡차(CAPTCHA)를 활용하여 반복적인 로그인 시도에 대한 일회성 확인 로직을 구현하여주시고, 자동화 공격을 감지하고 방어할 수 있는 IDS/IPS 시스템을 구축하여 주시기 바랍니다.", "countermeasure": "[대응 방안]\n웹 루트 디렉터리 내 웹 서비스에 불필요한 확장자(.bak, .backup, .org, .old, .zip, .log, .sql, .new, .txt, .tmp, .temp)가 존재하는지 확인 후 삭제하여 주시고, 웹 서버 설정 시 함께 제공되는 샘플 디렉터리 및 매뉴얼 디렉터리, 샘플 애플리케이션을 삭제하여 주시기 바랍니다."},
    "SN": {"name": "데이터 평문 전송", "result": "[대응 방안]\n주요정보통신기반시설 가이드를 참고하시어 httpd-ssl.conf 또는 ssl.conf의 SSL 관련 Virtual Host 설정을 'SSLProtocol all -SSLv2 -SSLv3 -TLSv1 -TLSv1.1'로 적용하여 주시기 바랍니다.", "countermeasure": "[대응 방안]\nhttpd-ssl.conf 또는 ssl.conf의 SSL 관련 VirtualHost 설정을 SSLProtocol all -SSLv2 -SSLv3 -TLSv1 -TLSv1.1로 변경하여 주시기 바랍니다."},
    "CC": {"name": "쿠키 변조", "countermeasure": "[대응 방안]\n쿠키에 저장되는 중요 정보는 암호화하고, 쿠키 대신 Server Side Session 방식을 사용하거나, 쿠키를 통해 인증 등 중요한 기능을 구현해야 할 경우엔 안전한 알고리즘(SEED, 3DES, AES 등) 적용하여 주시기 바랍니다."},
}


DB_NAME_MAP = {v['name']: k for k, v in DB_CODE_MAP.items()}
WEB_NAME_MAP = {v['name']: k for k, v in WEB_CODE_MAP.items()}

def normalize_db_code(s: str) -> str:
    """'D - 01', 'd01', 'D_1' 등도 'D-01'로 통일"""
    if not s:
        return ""
    s = str(s).upper().strip()
    m = re.search(r"D\s*[-_ ]?\s*(\d{1,2})", s)
    if not m:
        return s
    num = int(m.group(1))
    return f"D-{num:02d}"

POSITIVE_WORDS  = ["양호", "양호함", "적정"]
WEAKNESS_WORDS  = ["취약", "미흡", "취약함"]
INTERVIEW_WORDS = ["인터뷰", "인터뷰 필요", "보류", "추가 확인"]

def empty_state():
    return {"positive": False, "weakness": False, "interview": False}

def apply_state(result_val: str) -> Dict[str, bool]:
    """
    [수정됨] '취약' > '인터뷰' > '양호' 순서의 우선순위를 적용합니다.
    """
    txt = str(result_val)
    st = {"positive": False, "weakness": False, "interview": False}

    # 우선순위 1: '취약'이 발견되면, 무조건 '취약'으로 판정하고 즉시 종료
    if any(w in txt for w in WEAKNESS_WORDS):
        st["weakness"] = True
        return st

    # 우선순위 2: '취약'이 없고 '인터뷰'가 발견되면, '인터뷰'로 판정하고 즉시 종료
    if any(w in txt for w in INTERVIEW_WORDS):
        st["interview"] = True
        return st
    
    # 우선순위 3: '취약'과 '인터뷰'가 없을 때만 '양호'로 판정
    if any(w in txt for w in POSITIVE_WORDS):
        st["positive"]  = True
    
    return st

# [삭제됨] canon 함수가 제거되었습니다.

def normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", str(s)).strip()

# 파일 파서
HEADER_ALIASES = {
    "code": ["코드","항목코드","Code","code"],
    "item": ["항목명","점검항목","항목","Item","item"],
    "result": ["결과","진단결과","평가","Result","result"]
}

def find_col(df: pd.DataFrame, keys: List[str]) -> Optional[str]:
    for c in df.columns:
        c_norm = normalize_spaces(c)
        for k in keys:
            if k in c_norm:
                return c
    return None

def _detect_excel_engine(filename: str):
    ext = (filename or "").lower().rsplit(".", 1)[-1]
    if ext in ("xlsx", "xlsm", "xltx", "xltm"):
        return "openpyxl"
    if ext == "xls":
        return "xlrd"
    return "openpyxl"

def parse_report_from_excel(file, domain: str):
    file.file.seek(0)
    data = file.file.read()
    engine = _detect_excel_engine(file.filename)

    try:
        xls = pd.read_excel(io.BytesIO(data), sheet_name=None, header=2, dtype=str, engine=engine)
    except Exception:
        try:
            xls = pd.read_excel(io.BytesIO(data), sheet_name=None, header=1, dtype=str, engine=engine)
        except Exception:
            xls = pd.read_excel(io.BytesIO(data), sheet_name=None, header=0, dtype=str, engine=engine)

    codemap = DB_CODE_MAP if domain.upper() == "DB" else WEB_CODE_MAP
    results = {code: {"name": data['name'], **empty_state()} for code, data in codemap.items()}

    for sheet_name, df in xls.items():
        if df is None or df.empty:
            continue
            
        df = df.fillna("")
        col_code   = find_col(df, HEADER_ALIASES["code"])
        col_item   = find_col(df, HEADER_ALIASES["item"])
        col_result = find_col(df, HEADER_ALIASES["result"])
        
        if not col_result or not col_item: 
            continue

        if col_code: df[col_code] = df[col_code].replace("", pd.NA).ffill()
        df[col_item] = df[col_item].replace("", pd.NA).ffill()

        for _, row in df.iterrows():
            code_val   = normalize_spaces(row[col_code])   if col_code   else ""
            item_val   = normalize_spaces(row[col_item])   if col_item   else ""
            result_val = normalize_spaces(row[col_result]) if col_result else ""

            st = apply_state(result_val)
            if not any(st.values()):
                continue

            matched_code = None

            if code_val:
                key = normalize_db_code(code_val) if domain.upper() == "DB" else code_val.upper()
                if key in codemap:
                    matched_code = key

            if not matched_code and item_val:
                name_map = DB_NAME_MAP if domain.upper() == "DB" else WEB_NAME_MAP
                for name, code in name_map.items():
                    # [수정됨] canon() 대신 .lower()와 'in' 연산자로 단순 비교
                    if name.lower() in item_val.lower():
                        matched_code = code
                        break

            if matched_code:
                # [수정됨] 이전 대화의 우선순위 로직을 여기에 적용
                current_st = st 
                existing_st = results[matched_code]

                if current_st["weakness"]:
                    existing_st["weakness"] = True
                    existing_st["positive"] = False
                    existing_st["interview"] = False
                
                elif current_st["interview"] and not existing_st["weakness"]:
                    existing_st["interview"] = True
                    existing_st["positive"] = False

                elif current_st["positive"] and not existing_st["weakness"] and not existing_st["interview"]:
                    existing_st["positive"] = True

    return [{"id": code, **data} for code, data in results.items()]

def add_countermeasures_to_weaknesses(structured_results: List[Dict], domain: str) -> List[Dict]:
    """
    structured_results 리스트를 받아 '취약(weakness)' 상태인 항목에만
    대응 방안(countermeasure) 정보를 '추가'합니다.
    이 함수는 원본 리스트를 직접 수정합니다.

    Args:
        structured_results (List[Dict]): 분석 결과가 담긴 딕셔너리의 리스트.
        domain (str): 분석 대상 도메인 ("DB" 또는 "WEB").

    Returns:
        List[Dict]: 취약 항목에 대응 방안이 추가된, 수정된 리스트.
    """
    code_map = DB_CODE_MAP if domain.upper() == "DB" else WEB_CODE_MAP

    for item in structured_results:
        if item.get('weakness'):
            item_id = item.get('id')
            vulnerability_details = code_map.get(item_id)
            
            if vulnerability_details:
                item['countermeasure'] = vulnerability_details.get('countermeasure', '대응 방안 정보가 없습니다.')
    
    return structured_results

def parse_report_auto(file, domain: str) -> str:   
    """
    파일을 파싱하여 진단 결과를 추출하고, 취약점에 대응 방안을 추가하여 반환하는
    메인 진입점 함수입니다.
    """
    structured_results = parse_report_from_excel(file, domain)
    summary_output = add_countermeasures_to_weaknesses(structured_results, domain)
    return summary_output

def get_items() -> Dict[str, List[Dict[str, str]]]:
    """
    프론트엔드에서 사용할 수 있는 형태로 진단 항목 목록을 가공하여 반환합니다.
    """
    db_list = [{"id": code, **data} for code, data in DB_CODE_MAP.items()]
    web_list = [{"id": code, **data} for code, data in WEB_CODE_MAP.items()]
    return {"db": db_list, "web": web_list}