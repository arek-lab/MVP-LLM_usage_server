import json
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.loveable_features.utils.process_graphs import process_candidates_with_batching, DateTimeEncoder
from pydantic import BaseModel

class ProcessRequest(BaseModel):
    candidates: list[dict]
    max_concurrent: int = 15
    batch_size: int = 20

router = APIRouter()

@router.post("/")
async def process_candidates_endpoint(req: ProcessRequest):
    grouped = await process_candidates_with_batching(
        req.candidates,
        max_concurrent=req.max_concurrent,
        batch_size=req.batch_size
    )
    return JSONResponse(
        content=json.loads(
            json.dumps(grouped, cls=DateTimeEncoder)
        )
    )