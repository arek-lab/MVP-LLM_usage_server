import json
from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from app.loveable_features.utils.process_graphs import process_candidates_with_batching, DateTimeEncoder
from pydantic import BaseModel
from typing import List
from app.auth.utils import get_current_user
from app.auth.database import get_user_database

class ProcessRequest(BaseModel):
    candidates: list[dict]
    max_concurrent: int = 15
    batch_size: int = 20

class OriginalMessage(BaseModel):
    username: str
    timestamp: str
    message: str
    has_images: bool
    is_forwarded: bool
    role: str
    skip: bool
    auto_reject_reason: str | None
    needs_help_score: float


class MessageResponse(BaseModel):
    original_message: OriginalMessage | None = None
    message: str | None = None
    user: str | None = None
    is_lead: bool | None = None
    rag_insight: str | None = None
    reply: str


class ProcessResponse(BaseModel):
    leads: List[MessageResponse]
    no_leads: List[MessageResponse]
    errors: list
    credits: int

router = APIRouter()

@router.post("/")
async def process_candidates_endpoint(
    req: ProcessRequest,
    request: Request,
    current_user=Depends(get_current_user)):

    credits = current_user.credits
    if credits <= 20:
        return ProcessResponse(
            leads=[],
            no_leads=[],
            errors=[{"detail": "Niewystarczająca liczba kredytów"}]
        )   
    
    user_db = get_user_database(request)
    
    grouped = await process_candidates_with_batching(
        req.candidates,
        max_concurrent=req.max_concurrent,
        batch_size=req.batch_size
    )

    try:
        updated_user = await user_db.increment_credits(current_user.id, grouped["total_credits"])
        new_credits = updated_user.credits if updated_user else credits - grouped["total_credits"]
    except ValueError as e:
        return ProcessResponse(
            leads=[],
            no_leads=[],
            errors=[{"detail": "Wystąpił błąd weryfikacji kredytów"}],
            credits=0
        )   
    
    response = {
        **grouped["results"],
        "credits": new_credits
    }

    return JSONResponse(
        content=json.loads(
            json.dumps(response, cls=DateTimeEncoder)
        )
    )