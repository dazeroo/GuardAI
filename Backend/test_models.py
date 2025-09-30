from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("✗ API 키가 설정되지 않았습니다")
    exit(1)

print(f"✓ API 키 확인됨")
genai.configure(api_key=api_key)

print("\n사용 가능한 모델 목록:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  - {model.name}")
