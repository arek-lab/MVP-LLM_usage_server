from typing import Optional
from pydantic import BaseModel, Field

class LLMResponseModel(BaseModel):
    """Structured output dla rewrite chain"""
    text: str = Field(description="Przepisany tekst")
    confidence: Optional[float] = Field(
        default=None, 
        description="Pewność jakości przepisania (0-1), gdzie 1 = idealne"
    )