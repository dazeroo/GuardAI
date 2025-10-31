import logging
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.v2.mng_auto_diagnose_service import analyze_guideline

logger = logging.getLogger(__name__)
bp = Blueprint('diagnose', __name__, url_prefix="/api")

@bp.route("/diagnose", methods=["POST"])
def diagnose():
    if 'guideline' not in request.files:
        logger.warning("파일이 업로드되지 않았습니다.")
        return jsonify({"error": "파일이 업로드되지 않았습니다."}), 400

    files = request.files.getlist('guideline')
    if not files or all(f.filename == '' for f in files):
        logger.warning("빈 파일 이름이 제출되었습니다.")
        return jsonify({"error": "파일이 선택되지 않았습니다."}), 400

    all_guideline_texts = []
    processed_files = []
    failed_files = []

    for file in files:
        if file.filename == '':
            continue

        guideline_text, filename = extract_text_from_file(file, logger)
        if guideline_text and guideline_text.strip():
            all_guideline_texts.append(f"\n\n=== 파일명: {filename} ===\n{guideline_text}")
            processed_files.append(filename)
        else:
            failed_files.append(filename)
            logger.warning(f"파일 '{filename}'에서 텍스트를 추출할 수 없습니다.")

    if not all_guideline_texts:
        logger.warning("모든 파일이 비어있거나 읽을 수 있는 텍스트가 없습니다.")
        return jsonify({"error": "업로드된 파일에서 읽을 수 있는 텍스트가 없습니다.", "failed_files": failed_files}), 400

    combined_guideline_text = "\n".join(all_guideline_texts)
    try:
        diagnosis_data = perform_diagnosis(processed_files, combined_guideline_text, logger)
        if diagnosis_data is None:
            return jsonify({"error": "진단 결과에서 유효한 형식을 찾지 못했습니다."}), 500
        return jsonify({
            "data": diagnosis_data,
            "processed_files": processed_files,
            "failed_files": failed_files,
            "total_files": len(files)
        })
    except Exception as e:
        logger.error(f"진단 보고서 생성 중 오류 발생: {e}", exc_info=True)
        return jsonify({"error": "진단 보고서 생성 중 서버 오류가 발생했습니다."}), 500
