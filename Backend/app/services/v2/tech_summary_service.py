import pandas as pd
import re, io
from typing import List, Dict, Optional

DB_CODE_MAP = {
    "D-01": {"name": "기본 계정의 패스워드, 권한 등을 변경하여 사용", "countermeasure": "추측하기 어려운 복잡한 패스워드를 사용하고, 불필요한 기본 계정은 비활성화합니다."},
    "D-02": {"name": "데이터베이스의 불필요 계정을 제거하거나, 잠금설정 후 사용", "countermeasure": "사용하지 않는 계정은 즉시 삭제하거나 잠금 처리하여 비인가 접근을 차단합니다."},
    "D-03": {"name": "패스워드의 사용기간 및 복잡도를 기관 정책에 맞도록 설정", "countermeasure": "패스워드 최소 길이, 복잡도, 주기적 변경 정책을 수립하고 데이터베이스에 적용합니다."},
    "D-04": {"name": "데이터베이스 관리자 권한을 꼭 필요한 계정 및 그룹에 허용", "countermeasure": "DBA 권한은 최소한의 인원에게만 부여하고, 역할 기반의 접근 제어를 적용합니다."},
    "D-05": {"name": "원격에서 DB 서버로의 접속 제한", "countermeasure": "방화벽을 사용하여 허용된 IP 주소에서만 데이터베이스 포트로 접근을 허용하고, 불필요한 원격 접속은 차단합니다."},
    "D-06": {"name": "DBA 이외의 인가되지 않은 사용자 시스템 테이블에 접근할 수 없도록 설정", "countermeasure": "시스템 테이블 및 데이터 딕셔너리에 대한 접근 권한을 최소화하고, DBA 및 필수 역할에만 접근을 허용합니다."},
    "D-07": {"name": "오라클 데이터베이스의 경우 리스너의 패스워드를 설정하여 사용", "countermeasure": "Oracle Net Listener에 강력한 패스워드를 설정하여 비인가된 원격 관리를 방지합니다."},
    "D-08": {"name": "응용프로그램 또는 DBA 계정의 Role이 Public으로 설정되지 않도록 조정", "countermeasure": "PUBLIC 롤에 부여된 불필요한 권한을 회수하고, 각 계정에는 최소한의 필수 권한만 부여합니다."},
    "D-09": {"name": "OS_ROLES, REMOTE_OS_AUTHENTICATION, REMOTE_OS_ROLES를 FALSE로 설정", "countermeasure": "데이터베이스 파라미터 파일에서 해당 값들을 FALSE로 설정하여 운영체제 인증을 비활성화하고 데이터베이스 자체 인증을 사용합니다."},
    "D-10": {"name": "데이터베이스에 대해 최신 보안패치와 밴더 권고사항을 모두 적용", "countermeasure": "정기적으로 데이터베이스 벤더가 제공하는 보안 패치 및 업데이트를 확인하고 신속하게 적용합니다."},
    "D-11": {"name": "데이터베이스의 접근, 변경, 삭제 등의 감사기록이 기관의 감사기록 정책에 적합하도록 설정", "countermeasure": "로그인 시도, DDL/DML 작업 등 주요 활동에 대한 감사를 활성화하고, 감사 로그를 정기적으로 검토 및 보관합니다."},
    "D-12": {"name": "패스워드 재사용에 대한 제약 설정", "countermeasure": "데이터베이스의 패스워드 정책을 통해 사용자가 이전에 사용했던 패스워드를 일정 기간 재사용할 수 없도록 제한합니다."},
    "D-13": {"name": "DB 사용자 계정을 개별적으로 부여하여 사용", "countermeasure": "공용 계정 사용을 금지하고, 모든 사용자에게 개인별 계정을 발급하여 책임 추적성을 확보합니다."},
    "D-14": {"name": "불필요한 ODBC/OLE-DB 데이터 소스와 드라이브를 제거하여 사용", "countermeasure": "시스템에 설치된 데이터 소스 및 드라이버를 검토하여 사용하지 않는 항목은 삭제하여 공격 표면을 줄입니다."},
    "D-15": {"name": "일정 횟수의 로그인 실패 시 이에 대한 잠금정책이 설정", "countermeasure": "지정된 횟수 이상 로그인에 실패한 계정은 일정 시간 동안 자동으로 잠기도록 데이터베이스 보안 정책을 설정합니다."},
    "D-16": {"name": "데이터베이스의 주요 파일 보호 등을 위해 DB 계정의 umask를 022 이상으로 설정하여 사용", "countermeasure": "데이터베이스 소프트웨어 소유자 계정의 umask 값을 022 이상으로 설정하여, 새로 생성되는 파일의 기본 권한을 제한합니다."},
    "D-17": {"name": "데이터베이스의 주요 설정파일, 패스워드 파일 등과 같은 주요 파일들의 접근 권한이 적절하게 설정", "countermeasure": "데이터베이스 관련 중요 파일들의 소유자와 권한을 주기적으로 점검하고, 인가된 관리자 외에는 접근할 수 없도록 제한합니다."},
    "D-18": {"name": "관리자 이외의 사용자가 오라클 리스너의 접속을 통해 리스너 로그 및 trace 파일에 대한 변경 제한", "countermeasure": "리스너 로그 및 트레이스 파일의 권한을 관리자만 쓸 수 있도록 설정하고, 리스너의 원격 관리 기능을 비활성화합니다."},
    "D-19": {"name": "패스워드 확인함수가 설정되어 적용", "countermeasure": "데이터베이스에서 제공하는 패스워드 복잡도 검증 함수를 활성화하여 사용자가 정책에 맞는 강력한 패스워드를 설정하도록 강제합니다."},
    "D-20": {"name": "인가되지 않은 Object Owner의 제한", "countermeasure": "데이터베이스 객체는 반드시 정해진 소유자(스키마) 하에 생성되도록 관리하고, 불필요한 계정이 객체를 소유하지 않도록 통제합니다."},
    "D-21": {"name": "인가되지 않은 GRANT OPTION 사용 제한", "countermeasure": "WITH GRANT OPTION을 사용하여 권한을 부여하는 것을 최소화하고, 꼭 필요한 경우에만 제한적으로 사용하여 권한 남용을 방지합니다."},
    "D-22": {"name": "데이터베이스의 자원 제한 기능을 TRUE로 설정", "countermeasure": "RESOURCE_LIMIT 파라미터를 TRUE로 설정하고 프로파일을 통해 사용자별 자원 사용량을 제한하여 서비스 거부 공격 등을 방지합니다."},
    "D-23": {"name": "보안에 취약하지 않은 버전의 데이터베이스를 사용", "countermeasure": "벤더의 지원이 종료된(EOL) 버전 사용을 중단하고, 안정성과 보안이 검증된 최신 버전의 데이터베이스로 업그레이드합니다."},
    "D-24": {"name": "Audit Table은 데이터베이스 관리자 계정에 접근하도록 제한", "countermeasure": "감사 테이블에 대한 접근 권한을 DBA 역할이나 감사 관리자에게만 부여하고, 일반 사용자의 접근은 제한합니다."},
}

WEB_CODE_MAP: Dict[str, dict] = {
    "BO": {"name": "버퍼 오버플로우", "countermeasure": "웹 애플리케이션에 전달되는 파라미터 값을 필요한 크기만큼만 받을 수 있도록 변경하고 입력 값 범위를 초과한 경우에도 에러 페이지를 반환하지 않도록 설정합니다."},
    "FS": {"name": "포맷스트링", "countermeasure": "웹 서버 프로그램을 최신 버전으로 업데이트하고 포맷 스트링 버그를 발생시키는 문자열에 대한 검증 로직을 구현합니다."},
    "LI": {"name": "LDAP 인젝션", "countermeasure": "LDAP 쿼리 생성 시 사용자 입력을 이스케이프(escape) 처리하고, 지정된 문자열만 입력 허용합니다."},
    "OC": {"name": "운영체제 명령 실행", "countermeasure": '취약한 버전의 웹 서버 및 웹 애플리케이션 서버는 최신 버전으로 업데이트를 적용해야 하며, 입력 값에 대한 파라미터 데이터의  "&", "|", ";", "`" 문자에 대한 필터링 처리해야 합니다.'},
    "SI": {"name": "SQL 인젝션", "countermeasure": "파라미터화된 쿼리(Prepared Statement)를 사용하고, 입력값에 대한 유효성을 검증하는 로직을 구현합니다."},
    "SS": {"name": "SSI 인젝션", "countermeasure": "웹 서버에서 SSI(Server-Side Includes)를 비활성화하거나, 입력 값에 대한 검증 로직을 구현합니다."},
    "XP": {"name": "XPath 인젝션", "countermeasure": "허용된 문자 이외의 모든 입력을 허용하지 않아야 하며, XPath 쿼리에 사용자가 값을 입력할 수 있는 경우, 엄격한 입력 값 검증을 통해 필요 문자만을 받아들이게 합니다."},
    "DI": {"name": "디렉터리 인덱싱", "countermeasure": "웹 서버 설정에서 디렉터리 리스팅 기능을 비활성화하고, 각 디렉터리에 기본 페이지(index.html 등)를 설정합니다. Apache 서버의 경우 httpd.conf 파일 내 DocumentRoot 항목의 Options에서 Indexes를 제거합니다."},
    "IN": {"name": "정보 누출", "countermeasure": "웹 사이트에 노출되는 중요정보는 마스킹을 적용해야 합니다."},
    "MC": {"name": "악성 콘텐츠", "countermeasure": "업로드되는 파일의 확장자, MIME 타입을 제한하고, 파일 내용을 검사하며, 웹 루트 외부의 안전한 경로에 저장합니다."},
    "XS": {"name": "크로스사이트 스크립팅", "countermeasure": "입력값 필터링 및 출력값 인코딩(HTML Encoding)을 적용하여 스크립트 실행을 방지합니다."},
    "PW": {"name": "약한 문자열 강도", "countermeasure": "취약한 계정 및 패스워드를 삭제하고, 사용자가 취약한 계정이나 패스워드를 등록하지 못하도록 패스워드 규정이 반영된 체크 로직을 회원가입, 정보변경, 패스워드 변경 등 적용 필요한 페이지에 모두 구현하여야 함"},
    "AU": {"name": "불충분한 인증", "countermeasure": "다중 인증(MFA)을 도입하고, 모든 중요 기능에 대해 접근 전 반드시 사용자 인증 절차를 거치도록 설계합니다."},
    "PR": {"name": "취약한 패스워드 복구", "countermeasure": "패스워드 복구 시 본인 확인 절차를 강화하고, 인증된 사용자 메일이나 SMS에서만 재설정된 패스워드를 확인할 수 있도록 조치합니다."},
    "CR": {"name": "크로스사이트 리퀘스트 변조", "countermeasure": "주요 요청에 대해 사용자의 재인증을 요구하고, HTTP 헤더의 Referer 검증 로직을 구현합니다. 또한 정상적인 요청과 비정상적인 요청을 구분할 수 있도록 Hidden Form을 사용하여 임의의 암호화된 토큰(세션 ID, Timestamp, nonce 등)을 추가하고 이 토큰을 검증하도록 설계합니다."},
    "SE": {"name": "세션 예측", "countermeasure": "예측 불가능한 복잡하고 긴 세션 ID를 생성하기 위해 암호학적으로 안전한 난수 생성기를 사용합니다."},
    "AZ": {"name": "불충분한 인가", "countermeasure": "사용자의 모든 요청에 대해 서버 측에서 해당 사용자가 요청된 기능에 접근할 권한이 있는지 명시적으로 확인합니다."},
    "SM": {"name": "불충분한 세션 만료", "countermeasure": "사용자가 활동이 없을 경우 일정 시간 후에 세션이 자동으로 만료되도록 타임아웃을 설정하고, 로그아웃 시 세션을 즉시 무효화합니다."},
    "SF": {"name": "세션 고정", "countermeasure": "사용자가 성공적으로 인증된 후에는 즉시 새로운 세션 ID를 발급하여 이전 세션을 무효화합니다."},
    "AT": {"name": "자동화 공격", "countermeasure": "로그인, 회원가입 등 주요 기능에 CAPTCHA를 도입하고, 동일 IP에서의 비정상적인 반복 요청을 탐지하고 차단합니다."},
    "PV": {"name": "프로세스 검증 누락", "countermeasure": "중요한 비즈니스 로직의 모든 단계를 서버 측에서 순차적으로 검증하여 사용자가 단계를 건너뛸 수 없도록 방지합니다."},
    "FU": {"name": "파일 업로드", "countermeasure": "업로드 파일의 확장자 및 타입을 화이트리스트 방식으로 제한하고, 서버 실행 권한이 없는 디렉터리에 저장합니다."},
    "FD": {"name": "파일 다운로드", "countermeasure": "다운로드 시 허용된 경로 이외의 디렉터리와 파일에 접근할 수 없도록 구현합니다."},
    "AD": {"name": "관리자 페이지 노출", "countermeasure": "관리자 페이지 URL을 추측하기 어렵게 변경하고, 특정 IP 대역에서만 접근을 허용하며, 강력한 인증을 적용합니다. 단, 부득이하게 관리자 페이지를 외부에 노출해야 하는 경우 관리자 페이지 로그인 시 2차 인증(otp, vpn, 인증서 등) 적용이 필요합니다."},
    "PT": {"name": "경로 추적", "countermeasure": "사용자 입력에서 '../' 와 같은 디렉터리 탐색 문자를 필터링하고, 파일 시스템 접근 시 경로를 검증합니다."},
    "LP": {"name": "위치 공개", "countermeasure": "시스템 경로, 설정 파일 위치 등 내부 정보가 오류 메시지나 소스 코드에 노출되지 않도록 수정합니다. 또한,  웹 루트 디렉터리 이하 모든 불필요한 파일 및 샘플 페이지를 삭제합니다."},
    "CT": {"name": "데이터 평문 전송", "countermeasure": "로그인 정보, 개인정보 등 모든 민감한 데이터는 SSL/TLS를 적용하여 암호화된 HTTPS 프로토콜을 통해 전송합니다."},
    "CK": {"name": "쿠키 변조", "countermeasure": "쿠키에 저장되는 중요 정보는 암호화하고, 쿠키 대신 Server Side Session 방식을 사용하거나, 쿠키를 통해 인증 등 중요한 기능을 구현해야 할 경우엔 안전한 알고리즘(SEED, 3DES, AES 등) 적용합니다."},
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
    txt = str(result_val)
    st = {"positive": False, "weakness": False, "interview": False}
    if any(w in txt for w in POSITIVE_WORDS):  st["positive"]  = True
    if any(w in txt for w in WEAKNESS_WORDS):  st["weakness"]  = True
    if any(w in txt for w in INTERVIEW_WORDS): st["interview"] = True
    return st

def canon(s: str) -> str:
    if s is None: return ""
    s = str(s)
    s = re.sub(r"[\s\(\)\[\]·.,/_-]+", "", s).lower()
    s = s.replace("누출", "노출")
    s = s.replace("crosssitescripting", "크로스사이트스크립팅")
    s = s.replace("csrf", "리퀘스트변조")  
    s = s.replace("xpath", "xpath")       
    return s

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
                    if canon(name) in canon(item_val):
                        matched_code = code
                        break

            if matched_code:
                results[matched_code].update(st)

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
