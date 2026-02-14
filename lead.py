from pydantic import BaseModel, PositiveInt
from typing import Optional

class RawLead(BaseModel):
    id: str
    email: str
    raw_note: str

class EnrichedData(BaseModel):
    industry: str
    size: PositiveInt
    intent: str

class EnrichedLead(BaseModel):
    id: str
    email: str
    enriched_data: Optional[EnrichedData] = None
    score: Optional[int] = None
    crm_action: Optional[str] = None