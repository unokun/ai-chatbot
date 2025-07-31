from pydantic import BaseModel

class CorrectionVariant(BaseModel):
    text: str
    type: str
    reason: str