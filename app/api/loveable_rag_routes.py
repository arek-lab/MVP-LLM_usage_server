from fastapi import APIRouter
from pydantic import BaseModel
from app.loveable_features.rag.rag import rag_query

class RAGRequest(BaseModel):
    query: str

class RAGResponse(BaseModel):
    query: str
    response: str | None

router = APIRouter()

@router.post("/")
async def process_rag(req: RAGRequest):
    response = await rag_query(req.query)
    return RAGResponse(
        query=req.query,
        response=response
    )