# modules/malicious_content.py
# -*- coding: utf-8 -*-
import io
import magic  # 확장자가 아니라 실제 파일 안에 있는 바이트를 보고 파일 형식 판별
from typing import Dict, Any

def test_malicious_content(target: str, session) -> Dict[str, Any]:
    """
    파일 업로드 검사: 확장자/내용 불일치, 실행가능 파일 허용 여부 확인
    """
    upload_paths = ['/upload', '/wp-admin/async-upload.php', '/file_upload']
    details = []
    suspicious = False

    # 샘플 파일: 확장자 .jpg지만 실제는 'PHP 코드'(무해화된 텍스트)
    php_like = b"<?php /* harmless test */ echo 'ok'; ?>"
    files = {
        'file': ('test.jpg', io.BytesIO(php_like), 'image/jpeg')
    }

    for p in upload_paths:
        url = target.rstrip('/') + p
        try:
            r = session.post(url, files=files, timeout=8, allow_redirects=False)
            code = r.status_code
            text = (r.text or "").lower()
            if code in (200,201,302) and ('php' in text or 'test.jpg' in text or 'upload' in text):
                suspicious = True
                details.append(f"[허용 가능성] {url} 가 확장자와 내용 불일치 파일을 허용 가능성 (응답 코드 {code})")
            # 추가: 업로드 후 접근 가능한 URL이 반환되면 그 URL에 GET 요청 시 200이면 의심
            # (리포트에 URL을 남기되 민감정보 주의)
        except Exception as e:
            details.append(f"[요청오류] {url} 업로드 실패: {e}")
    if suspicious:
        return {'status':'취약','description':'업로드 유효성 검증 미흡 의심','details':details}
    if details:
        return {'status':'인터뷰','description':'업로드 검사 중 일부 이상징후','details':details}
    return {'status':'양호','description':'업로드 검증(확장자/내용) 기본 검사 통과','details':[]}
