import os
import google.generativeai as genai
from app.models.ai_models import GenerateRequest, GenerateResponse
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import pandas as pd 
import json
from typing import Any

def to_json(sentence: str)->Any:
    return json.loads(sentence)
    

def get_data(server:str)->str:
    # 1. 데이터베이스 연결 URL 설정
    DATABASE_URL = os.environ.get(
        "DATABASE_URL", 
        f"sqlite:///{Path(__file__).resolve().parent.parent.parent.parent / 'app_data.db'}"
    )

    # 2. 데이터베이스 엔진 생성
    engine_args = {}
    if DATABASE_URL.startswith("sqlite"):
        engine_args["connect_args"] = {"check_same_thread": False}

    engine = create_engine(DATABASE_URL, **engine_args)
    sql = text(
    "SELECT * FROM files WHERE file_name LIKE :server "
    "ORDER BY uploaded_at DESC LIMIT 1"
    )
    df = pd.read_sql(sql, engine, params={"server": f"%{server}%"})
    cve_lists = []
    for row in to_json(df.summary_output[0]):
        if row['weakness']:
            cve_lists.append(row['name'])

    return ','.join(cve_lists)

async def generate_ai_response(req: GenerateRequest) -> GenerateResponse:
    # 프롬프트 준비
    cve_str = get_data(req.tabType)
    if req.tabType == "db":
        
        attack_desc = f"MySQL의 ({cve_str})"
    else:
        attack_desc = f"WordPress의 ({cve_str})"

    attack_desc += f"에서 취약점이 발생하였는데, 추가로 발생할 수 있는 공격 방법에 대해 3줄로 요약해서 간단하게 알려줘 (부연설명 제외)"

    # 모델 인스턴스 생성 및 비동기 호출로 변경
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    res1 = await model.generate_content_async(attack_desc)
    attack = res1.text

    yara_desc = attack + " 해당 공격 방법을 방어할 수 있는 yara 룰을 작성해줘 (부연설명 제외)"
    res2 = await model.generate_content_async(yara_desc)
    yara = res2.text

    return GenerateResponse(status="success", attack=attack, yara=yara)
