from fastapi import APIRouter, Depends, Request
from app.text_crafter.graph import graph
from app.text_crafter.schemas import UserInput
from app.text_crafter.state import State
from app.auth.utils import get_current_user
from app.auth.database import get_user_database
from app.text_crafter.schemas import ResponseModel

router = APIRouter()

@router.post("/")
async def craft_text(
    payload: UserInput, 
    request: Request,
    current_user=Depends(get_current_user)):

    credits = current_user.credits
    if credits <= 0:
      response = ResponseModel(
        confidence=0,
        output_MD='Liczba kredytów wynosi 0.',
        credtis=credits
        )
      return response


    state = State(**payload.model_dump())
    result: State = await graph.ainvoke(state)

    user_db = get_user_database(request)
    try:
        updated_user = await user_db.increment_credits(current_user.id, -1)
        new_credits = updated_user.credits if updated_user else credits - 1
    except ValueError as e:
        return ResponseModel(
            text= result["result"].text,
            confidence= result["result"].confidence,
            credits=0
            )

    return ResponseModel(
        text= result["result"].text,
        confidence= result["result"].confidence,
        credits=new_credits
        )

