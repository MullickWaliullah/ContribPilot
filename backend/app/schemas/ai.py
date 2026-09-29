from pydantic import BaseModel, Field


class HintResponse(BaseModel):
    level: int = Field(..., ge=1, le=3)
    hint_text: str = Field(..., min_length=1)