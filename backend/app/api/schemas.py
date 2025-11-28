from pydantic import BaseModel
from typing import Optional

class RawItem(BaseModel):
    source: str
    url: Optional[str]
    title: str
    summary: Optional[str]
    fetched_at: Optional[str]

class Claim(BaseModel):
    raw_id: str
    text: str
    extracted_at: Optional[str]
    status: Optional[str] = 'unverified'

class Verification(BaseModel):
    claim_id: str
    verdict: str  # 'true','false','mixture','unverified'
    score: float
    evidence: Optional[list] = []
    checked_at: Optional[str]
