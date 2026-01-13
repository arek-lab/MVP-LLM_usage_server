"""
Pydantic models for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class GraphStatus(str, Enum):
    """Graph execution status"""
    RUNNING = "running"
    WAITING_HITL = "waiting_hitl"
    COMPLETED = "completed"
    ERROR = "error"


class HITLType(str, Enum):
    """Types of HITL interrupts"""
    ADDITIONAL_INFO = "additional_info"
    ACCEPTATION = "acceptation"


# ===== START GRAPH =====

class GraphStartResponse(BaseModel):
    """Response after starting graph execution"""
    thread_id: str = Field(..., description="Unique thread identifier")
    status: str = Field(default="started", description="Initial status")
    message: str = Field(..., description="Status message"),
    credits: int | None


# ===== STATUS =====

class GraphStatusResponse(BaseModel):
    """Current graph execution status"""
    thread_id: str
    status: GraphStatus
    next_node: Optional[str] = Field(None, description="Next node to execute")
    hitl_type: Optional[HITLType] = Field(None, description="Type of HITL if waiting")
    hitl_data: Optional[Dict[str, Any]] = Field(None, description="Data needed for HITL")
    result: Optional[Dict[str, Any]] = Field(None, description="Final result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")


# ===== HITL FEEDBACK =====

class AdditionalInfoFeedback(BaseModel):
    """Feedback for additional CV information"""
    additional_info: str = Field(..., description="Additional information provided by user")


class AcceptationFeedback(BaseModel):
    """Feedback for CV data acceptation"""
    accepted_cv_data: Dict[str, Any] = Field(..., description="Accepted or modified CV data")


class HITLFeedbackRequest(BaseModel):
    """Generic HITL feedback request"""
    hitl_type: HITLType = Field(..., description="Type of HITL feedback")
    additional_info: Optional[str] = Field(None, description="For additional_info HITL")
    accepted_cv_data: Optional[Dict[str, Any]] = Field(None, description="For acceptation HITL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "hitl_type": "additional_info",
                "additional_info": "I also have experience with Python and FastAPI"
            }
        }


class HITLFeedbackResponse(BaseModel):
    """Response after submitting HITL feedback"""
    thread_id: str
    status: str = Field(default="resumed", description="Status after feedback")
    message: str = Field(..., description="Confirmation message")


# ===== STREAMING =====

class StreamEvent(BaseModel):
    """SSE event structure"""
    type: str = Field(..., description="Event type: node_update, status_change")
    data: Dict[str, Any] = Field(..., description="Event data")


# ===== ERROR =====

class ErrorResponse(BaseModel):
    """Error response structure"""
    detail: str = Field(..., description="Error details")
    thread_id: Optional[str] = Field(None, description="Thread ID if applicable")