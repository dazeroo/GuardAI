import os
from google import genai
from app.models.ai_models import GenerateRequest, GenerateResponse

async def generate_ai_response(req: GenerateRequest) -> GenerateResponse:
    my_key = os.environ.get("GENAI_API_KEY")
    if not my_key:
        raise ValueError("API key not configured")

    client = genai.Client(api_key=my_key)

    # 프롬프트 준비
    if req.tabType == "db":
        attack_desc = "MySQL의 "
    else:
        attack_desc = "WordPress의 "

    attack_desc += f"DB 접근 제어가 아닌 다른 취약점을 3줄로 요약해서 간단하게 알려줘 (부연설명 제외)"

    res1 = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=attack_desc
    )
    attack = getattr(res1.text, "failed", str(res1.text))

    yara_desc = attack + " 해당 취약점을 탐지할 수 있는 yara 룰을 작성해줘 (부연설명 제외)"
    res2 = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=yara_desc
    )
    yara = getattr(res2.text, "failed", str(res2.text))

    return GenerateResponse(status="success", attack=attack, yara=yara)
