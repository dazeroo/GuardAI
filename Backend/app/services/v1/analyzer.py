import pandas as pd
import re, io
from typing import List, Dict, Optional

# ------------------ 진단 항목 정의 ------------------

DB_ITEMS = [
    "기본 계정의 패스워드, 권한 등을 변경하여 사용",
    "데이터베이스의 불필요 계정을 제거하거나, 잠금설정 후 사용",
    "패스워드의 사용기간 및 복잡도를 기관 정책에 맞도록 설정",
    "데이터베이스 관리자 권한을 꼭 필요한 계정 및 그룹에 허용",
    "패스워드 재사용에 대한 제약 설정",
    "DB 사용자 계정을 개별적으로 부여하여 사용",
    "원격에서 DB 서버로의 접속 제한",
    "DBA 이외의 인가되지 않은 사용자 시스템 테이블에 접근할 수 없도록 설정",
    "오라클 데이터베이스의 경우 리스너의 패스워드를 설정하여 사용",
    "불필요한 ODBC/OLE-DB 데이터 소스와 드라이브를 제거하여 사용",
    "일정 횟수의 로그인 실패 시 이에 대한 잠금정책이 설정",
    "데이터베이스의 주요 파일 보호 등을 위해 DB 계정의 umask를 022 이상으로 설정하여 사용",
    "데이터베이스의 주요 설정파일, 패스워드 파일 등과 같은 주요 파일들의 접근 권한이 적절하게 설정",
    "관리자 이외의 사용자가 오라클 리스너의 접속을 통해 리스너 로그 및 trace 파일에 대한 변경 제한",
    "응용프로그램 또는 DBA 계정의 Role이 Public으로 설정되지 않도록 조정",
    "OS_ROLES, REMOTE_OS_AUTHENTICATION, REMOTE_OS_ROLES를 FALSE로 설정",
    "패스워드 확인함수가 설정되어 적용",
    "인가되지 않은 Object Owner의 제한",
    "인가되지 않은 GRANT OPTION 사용 제한",
    "데이터베이스의 자원 제한 기능을 TRUE로 설정",
    "데이터베이스에 대해 최신 보안패치와 밴더 권고사항을 모두 적용",
    "데이터베이스의 접근, 변경, 삭제 등의 감사기록이 기관의 감사기록 정책에 적합하도록 설정",
    "보안에 취약하지 않은 버전의 데이터베이스를 사용",
    "Audit Table은 데이터베이스 관리자 계정에 접근하도록 제한"
]

DB_CODE_MAP = {
    "D-01": "기본 계정의 패스워드, 권한 등을 변경하여 사용",
    "D-02": "데이터베이스의 불필요 계정을 제거하거나, 잠금설정 후 사용",
    "D-03": "패스워드의 사용기간 및 복잡도를 기관 정책에 맞도록 설정",
    "D-04": "데이터베이스 관리자 권한을 꼭 필요한 계정 및 그룹에 허용",
    "D-05": "원격에서 DB 서버로의 접속 제한",
    "D-06": "DBA 이외의 인가되지 않은 사용자 시스템 테이블에 접근할 수 없도록 설정",
    "D-07": "오라클 데이터베이스의 경우 리스너의 패스워드를 설정하여 사용",
    "D-08": "응용프로그램 또는 DBA 계정의 Role이 Public으로 설정되지 않도록 조정",
    "D-09": "OS_ROLES, REMOTE_OS_AUTHENTICATION, REMOTE_OS_ROLES를 FALSE로 설정",
    "D-10": "데이터베이스에 대해 최신 보안패치와 밴더 권고사항을 모두 적용",
    "D-11": "데이터베이스의 접근, 변경, 삭제 등의 감사기록이 기관의 감사기록 정책에 적합하도록 설정",
    "D-12": "패스워드 재사용에 대한 제약 설정",
    "D-13": "DB 사용자 계정을 개별적으로 부여하여 사용",
    "D-14": "불필요한 ODBC/OLE-DB 데이터 소스와 드라이브를 제거하여 사용",
    "D-15": "일정 횟수의 로그인 실패 시 이에 대한 잠금정책이 설정",
    "D-16": "데이터베이스의 주요 파일 보호 등을 위해 DB 계정의 umask를 022 이상으로 설정하여 사용",
    "D-17": "데이터베이스의 주요 설정파일, 패스워드 파일 등과 같은 주요 파일들의 접근 권한이 적절하게 설정",
    "D-18": "관리자 이외의 사용자가 오라클 리스너의 접속을 통해 리스너 로그 및 trace 파일에 대한 변경 제한",
    "D-19": "패스워드 확인함수가 설정되어 적용",
    "D-20": "인가되지 않은 Object Owner의 제한",
    "D-21": "인가되지 않은 GRANT OPTION 사용 제한",
    "D-22": "데이터베이스의 자원 제한 기능을 TRUE로 설정",
    "D-23": "보안에 취약하지 않은 버전의 데이터베이스를 사용",
    "D-24": "Audit Table은 데이터베이스 관리자 계정에 접근하도록 제한",
}

WEB_ITEMS = [
    "버퍼 오버플로우","포맷스트링","LDAP 인젝션","운영체제 명령 실행","SQL 인젝션","SSI 인젝션",
    "XPath 인젝션","디렉터리 인덱싱","정보 누출","악성 콘텐츠","크로스사이트 스크립팅",
    "약한 문자열 강도","불충분한 인증","취약한 패스워드 복구","크로스사이트 리퀘스트 변조(CSRF)",
    "세션 예측","불충분한 인가","불충분한 세션 만료","세션 고정","자동화 공격",
    "프로세스 검증 누락","파일 업로드","파일 다운로드","관리자 페이지 노출","경로 추적",
    "위치 공개","데이터 평문 전송","쿠키 변조"
]

WEB_CODE_MAP: Dict[str, str] = {
    "BO": "버퍼 오버플로우",
    "FS": "포맷스트링",
    "LI": "LDAP 인젝션",
    "OC": "운영체제 명령 실행",
    "SI": "SQL 인젝션",
    "SS": "SSI 인젝션",
    "XP": "XPath 인젝션",
    "DI": "디렉터리 인덱싱",
    "IN": "정보 누출",
    "MC": "악성 콘텐츠",
    "XS": "크로스사이트 스크립팅",
    "PW": "약한 문자열 강도",
    "AU": "불충분한 인증",
    "PR": "취약한 패스워드 복구",
    "CR": "크로스사이트 리퀘스트 변조(CSRF)",
    "SE": "세션 예측",
    "AZ": "불충분한 인가",
    "SM": "불충분한 세션 만료",
    "SF": "세션 고정",
    "AT": "자동화 공격",
    "PV": "프로세스 검증 누락",
    "FU": "파일 업로드",
    "FD": "파일 다운로드",
    "AD": "관리자 페이지 노출",
    "PT": "경로 추적",
    "LP": "위치 공개",
    "CT": "데이터 평문 전송",
    "CK": "쿠키 변조",
}

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
# ------------------ 상태 정의 ------------------

STATUS_MAP = {"양호": "positive", "취약": "weakness", "인터뷰": "interview"}
STATUS_KEYS = list(STATUS_MAP.keys())

# --- 결과 키워드(변형 포함) ---
POSITIVE_WORDS  = ["양호", "양호함", "적정"]
WEAKNESS_WORDS  = ["취약", "미흡", "취약함"]
INTERVIEW_WORDS = ["인터뷰", "인터뷰 필요", "보류", "추가 확인"]

def apply_state(result_val: str) -> Dict[str, bool]:
    txt = str(result_val)
    st = {"positive": False, "weakness": False, "interview": False}
    if any(w in txt for w in POSITIVE_WORDS):  st["positive"]  = True
    if any(w in txt for w in WEAKNESS_WORDS):  st["weakness"]  = True
    if any(w in txt for w in INTERVIEW_WORDS): st["interview"] = True
    return st

# --- 항목명 정규화: 공백/괄호/기호 제거, 대소문자 무시, 몇 가지 동의어 보정 ---
def canon(s: str) -> str:
    if s is None: return ""
    s = str(s)
    # 공백/괄호/기호 제거
    s = re.sub(r"[\s\(\)\[\]·.,/_-]+", "", s).lower()
    # 동의어/철자 보정
    s = s.replace("누출", "노출")
    s = s.replace("crosssitescripting", "크로스사이트스크립팅")
    s = s.replace("csrf", "리퀘스트변조")  # (CSRF) 유무 차이 흡수
    s = s.replace("xpath", "xpath")       # 대소문자 무시
    return s


# ------------------ 유틸 ------------------

def normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", str(s)).strip()

def no_space(s: str) -> str:
    return re.sub(r"\s+", "", str(s))

def variants(name: str) -> List[str]:
    return [name, no_space(name)]

def _detect_header_and_set_columns(df_raw: pd.DataFrame) -> Optional[pd.DataFrame]:
    # 앞 10행 안에서 '항목명/결과/코드' 문구가 보이는 줄을 헤더로 사용
    max_scan = min(10, len(df_raw))
    for hr in range(max_scan):
        row_vals = df_raw.iloc[hr].fillna("").astype(str).tolist()
        row_join = " ".join(row_vals)
        if any(k in row_join for k in HEADER_ALIASES["item"] + HEADER_ALIASES["result"] + HEADER_ALIASES["code"]):
            df = df_raw.iloc[hr+1:].copy()   # 헤더 아래부터 데이터
            df.columns = row_vals            # 해당 줄을 컬럼으로 지정
            return df.fillna("")
    return None


# ------------------ 파일 파서 ------------------

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

    # header=2 로 바로 읽기 (엑셀 3행이 헤더일 경우)
    try:
        xls = pd.read_excel(io.BytesIO(data), sheet_name=None, header=2, dtype=str, engine=engine)
    except ValueError:
        alt = "xlrd" if engine == "openpyxl" else "openpyxl"
        xls = pd.read_excel(io.BytesIO(data), sheet_name=None, header=2, dtype=str, engine=alt)

    items   = DB_ITEMS if domain.upper() == "DB" else WEB_ITEMS
    codemap = DB_CODE_MAP if domain.upper() == "DB" else WEB_CODE_MAP
    
    if domain.upper() == "DB":
        items   = DB_ITEMS
        codemap = DB_CODE_MAP
    else:
        items   = WEB_ITEMS
        codemap = WEB_CODE_MAP

    results = {name: {"positive": False, "weakness": False, "interview": False} for name in items}

    for sheet_name, df in xls.items():
        if df is None or df.empty:
            continue
        df = df.fillna("")

        col_code   = find_col(df, HEADER_ALIASES["code"])
        col_item   = find_col(df, HEADER_ALIASES["item"])
        col_result = find_col(df, HEADER_ALIASES["result"])
        if not col_result:
            continue

        # 🔹 병합셀 보정: 비어있는 코드/항목명은 위 값으로 채움
        for c in [col_code, col_item]:
            if c:
                df[c] = df[c].replace("", pd.NA).ffill()

        for _, row in df.iterrows():
            code_val   = normalize_spaces(row[col_code])   if col_code   else ""
            item_val   = normalize_spaces(row[col_item])   if col_item   else ""
            result_val = normalize_spaces(row[col_result]) if col_result else ""

            st = apply_state(result_val)
            if not any(st.values()):
                continue

            matched = None

            # ✅ 코드 우선(특히 DB): 정규화하여 매핑
            if code_val and codemap:
                key = normalize_db_code(code_val) if domain.upper() == "DB" else code_val
                if key in codemap:
                    matched = codemap[key]

            # 보조: 항목명 매칭 (정확/부분/정규화 유사)
            if not matched and item_val:
                for name in items:
                    if name in item_val:
                        matched = name; break
                if not matched:
                    cv = canon(item_val)
                    for name in items:
                        if canon(name) in cv or cv in canon(name):
                            matched = name; break

            if matched and matched in results:
                results[matched] = st


    return [{"name": k, **v} for k, v in results.items()]

# ------------------ 텍스트 보고서 ------------------

def read_text(file) -> str:
    name = (file.filename or "").lower()
    data = file.file.read()
    if name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    elif name.endswith(".docx"):
        import docx
        doc = docx.Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        return data.decode(errors="ignore")

def status_in(text: str) -> Optional[str]:
    for word in STATUS_KEYS:
        if word in text:
            return word
    return None

def line_window(lines: List[str], idx: int) -> str:
    cur = normalize_spaces(lines[idx])
    nxt = normalize_spaces(lines[idx+1]) if idx+1 < len(lines) else ""
    nxt2 = normalize_spaces(lines[idx+2]) if idx+2 < len(lines) else ""
    return f"{cur} {nxt} {nxt2}".strip()

def parse_report_from_text(text: str, domain: str):
    items = DB_ITEMS if domain.upper() == "DB" else WEB_ITEMS
    code_map = {} if domain.upper() == "DB" else WEB_CODE_MAP
    lines = text.splitlines()
    out = []

    for item in items:
        st = empty_state()
        matched = False

        # 항목명 매칭
        for i in range(len(lines)):
            chunk = line_window(lines, i)
            if any(v in no_space(chunk) for v in map(no_space, variants(item))):
                w = status_in(chunk)
                if w:
                    st = empty_state(); st[STATUS_MAP[w]] = True
                    matched = True
                    break
        # 코드 매칭
        if not matched and code_map:
            for i in range(len(lines)):
                chunk = line_window(lines, i)
                m = re.search(r"\b([A-Z]{1,3})\b", chunk)
                if m and code_map.get(m.group(1)) == item:
                    w = status_in(chunk)
                    if w:
                        st = empty_state(); st[STATUS_MAP[w]] = True
                        break

        out.append({"name": item, **st})
    return out

# ------------------ 엔트리 함수 ------------------

def parse_report_auto(file, domain: str):
    filename = file.filename or ""
    file.file.seek(0)
    if filename.lower().endswith((".xlsx", ".xls")):
        return parse_report_from_excel(file, domain)
    file.file.seek(0)
    text = read_text(file)
    return parse_report_from_text(text, domain)
