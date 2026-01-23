from typing import TypedDict, List

from pydantic import BaseModel


class Flags(TypedDict):
    contains_profanity: bool
    is_all_caps: bool
    has_excessive_punctuation: bool

class RewriteResult(BaseModel):
    """Wynik przepisania tekstu"""
    text: str 
    subcategory_used: str  
    confidence: float | None

class QualityCheckResult(BaseModel):
        passed: bool
        score: float
        issues: List[str]
        suggestions: List[str]
    

class State(TypedDict):
    original_text: str
    current_text: str | None
    flags: Flags | None
    intent: str
    subcategory: str | None
    options: dict | None
    result: RewriteResult | None
    quality_result: QualityCheckResult | None
