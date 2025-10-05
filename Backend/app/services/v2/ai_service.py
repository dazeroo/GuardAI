import os
import google.generativeai as genai
from app.models.ai_models import GenerateRequest, GenerateResponse

async def generate_ai_response(req: GenerateRequest) -> GenerateResponse:
    # 프롬프트 준비
    if req.tabType == "db":
        attack_desc = "MySQL의 "
    else:
        attack_desc = "WordPress의 "

    attack_desc += f"DB 접근 제어가 아닌 다른 취약점을 3줄로 요약해서 간단하게 알려줘 (부연설명 제외)"

    # 모델 인스턴스 생성 및 비동기 호출로 변경
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    res1 = await model.generate_content_async(attack_desc)
    attack = res1.text

    yara_desc = attack + " 해당 취약점을 탐지할 수 있는 yara 룰을 작성해줘 (부연설명 제외)"
    res2 = await model.generate_content_async(yara_desc)
    yara = res2.text

    return GenerateResponse(status="success", attack=attack, yara=yara)