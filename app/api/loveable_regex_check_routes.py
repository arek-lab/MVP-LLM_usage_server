from fastapi import APIRouter, Request, UploadFile, File, HTTPException, Depends
from app.loveable_features.regex_check.filters import process_messages
from app.auth.utils import get_current_user

router = APIRouter()


@router.post("/")
async def process_messages_route(
    request: Request, 
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Wymagany plik .txt")

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Plik musi być w kodowaniu UTF-8")

    candidates, all_messages = await process_messages(request, text)

    return {
        "candidates_count": len(candidates),
        "total_count": len(all_messages),
        "candidates": candidates,
        "rejected": [m for m in all_messages if m["skip"]]
    }