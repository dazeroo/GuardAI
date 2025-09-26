from pydantic import BaseModel
from typing import Literal

class GenerateRequest(BaseModel):
    tabType: Literal["db", "web"]

class GenerateResponse(BaseModel):
    status: str
    attack: str
    yara: str
