from typing import TypedDict, Annotated, Literal
from langgraph.graph.message import add_messages, AnyMessage
from app.graph.chains.cv_data_model import CVData
from app.graph.chains.compare_cv_to_offer import ComparisonResult
from pydantic import BaseModel, Field

from app.graph.chains.job_description_model import JobDescription

class AdditionalInfoHumanFeedback(BaseModel):
    additional_info: str | None 
    removal_acceptance: bool = False
    
class FileResult(BaseModel):
    """Model reprezentujący wygenerowany plik PDF"""
    
    type: Literal["file"] = "file"
    file_id: str = Field(
        ...,
        min_length=36,
        max_length=36
    )
    download_url: str = Field(
        ...,
        description="URL do pobrania pliku",
    )
    filename: str = Field(
        ...,
        description="Nazwa pliku do pobrania",
    )
    size: int = Field(
        ...,
        gt=0
    )
    format: Literal["pdf"] = "pdf"
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "file",
                "file_id": "123e4567-e89b-12d3-a456-426614174000",
                "download_url": "/api/cv/download/123e4567-e89b-12d3-a456-426614174000",
                "filename": "CV.pdf",
                "size": 245678,
                "format": "pdf",
                "created_at": "2024-12-17T10:30:00"
            }
        }

class State(TypedDict):
    cv_text: str
    job_offer: str | None
    extracted_cv: CVData | None
    job_offer_description: JobDescription | None
    job_offer_agent_messages: Annotated[list[AnyMessage], add_messages]
    comparison_result: ComparisonResult | None
    additional_info_human_feedback: AdditionalInfoHumanFeedback | None
    accepted_cv_data: CVData | None
    html_structure: str | None
    final_html: str | None
    pdf_result: FileResult | None

