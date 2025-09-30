from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if api_key:
    print(f"✓ API 키 설정됨 (길이: {len(api_key)}자)")
    print(f"  첫 10자: {api_key[:10]}...")
else:
    print("✗ API 키가 설정되지 않았습니다")
EOF
