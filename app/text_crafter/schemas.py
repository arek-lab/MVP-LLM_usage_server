from enum import Enum
from pydantic import BaseModel, Field

class Intent(str, Enum):
    REWRITE_FLOW = "rewrite_flow"
    SHORTEN_FLOW = "shorten_flow"
    TONE_FLOW = "tone_flow"
    SIMPLIFY_FLOW = "simplify_flow"

class Subcategory(str, Enum):
    # Podkategorie z chains/rewrite/prompts.py
    FORMAL_TO_INFORMAL = "formal_to_informal"
    INFORMAL_TO_FORMAL = "informal_to_formal"
    IMPROVE_CLARITY = "improve_clarity"
    AUDIENCE_ADAPTATION = "audience_adaptation"
    CREATIVE_REPHRASE = "creative_rephrase"
    PLATFORM_ADAPTATION = "platform_adaptation"
    EXPAND = "expand"
    MAKE_PERSUASIVE = "make_persuasive"
    PASSIVE_TO_ACTIVE = "passive_to_active"
    GENERAL = "general"

    # Podkategorie ze skracania (shorten)
    BRIEF_SUMMARY = "brief_summary"
    REMOVE_FLUFF = "remove_fluff"
    KEY_POINTS = "key_points"
    EXECUTIVE_SUMMARY = "executive_summary"

    # Podkategorie z upraszczania (simplify)
    REDUCE_JARGON = "reduce_jargon"
    SHORTER_SENTENCES = "shorter_sentences"
    EVERYDAY_LANGUAGE = "everyday_language"
    EXPLAIN_CONCEPTS = "explain_concepts"
    LOWER_READING_LEVEL = "lower_reading_level"

class UserInput(BaseModel):
    original_text: str = Field(..., description="Tekst wejściowy do przetworzenia przez LLM")
    intent: Intent
    subcategory: Subcategory = Field(..., description="Wybrana podkategoria operacji")
    options: dict | None

    class Config:
        schema_extra = {
            "example": {
                "content": "Szanowni Państwo, uprzejmie informujemy o zmianie regulaminu.",
                "subcategory": "formal_to_informal",
                "preserve_tone": True
            }
        }

class ResponseModel(BaseModel):
    text: str
    confidence: float
    credits: int