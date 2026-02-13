from pydantic import BaseModel

class RawLead(BaseModel):
    id: str
    email: str
    raw_note: str