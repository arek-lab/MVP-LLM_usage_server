from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from app.loveable_features.rag.rag import rag_query
from app.auth.utils import get_current_user
from app.auth.database import get_user_database

class RAGRequest(BaseModel):
    query: str

class RAGResponse(BaseModel):
    query: str
    response: str | None
    credits: int

router = APIRouter()

@router.post("/")
async def process_rag(
    req: RAGRequest,
    request: Request,
    current_user=Depends(get_current_user)):

    credits = current_user.credits
    if credits <= 0:
        response = RAGResponse(
            query=req.query,
            response='Liczba kredytów wynosi 0.',
            credtis=credits
            )
        return response

    user_db = get_user_database(request)

    response = await rag_query(req.query)

    try:
        updated_user = await user_db.increment_credits(current_user.id, -1)
        new_credits = updated_user.credits if updated_user else credits - 1
    except ValueError as e:
        return RAGResponse(
            query=req.query,
            response=response,
            credtis=0
            )

    return RAGResponse(
        query=req.query,
        response=response,
        credits=new_credits
    )