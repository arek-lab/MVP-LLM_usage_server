from fastapi import APIRouter, Depends, Request
from app.auth.utils import get_current_user
from app.services.feedback_service import get_feedback
from app.services.feedback.schemas import UserData
from app.auth.database import get_user_database

router = APIRouter()


@router.post("/")
async def feedback_generator(
    request: Request,
    user_data: UserData, 
    current_user=Depends(get_current_user)
):
    credits = current_user.credits
    if credits <= 0:
        return {
            "feedback": 'Liczba kredytów wynosi 0.',
            "metadata": {
                "development_level": '',
                "recommended_style": '',
                "applied_style": '',
                "is_aligned": False,
                "warning": False,
                "tokens": {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                },
                "credits": credits
            },
        }
    
    response = await get_feedback(
        message=user_data.userQuery,
        s_level=user_data.leadershipStyle,
        d_level=user_data.developmentLevel,
    )
    
    # Aktualizacja kredytów
    user_db = get_user_database(request)
    try:
        updated_user = await user_db.increment_credits(current_user.id, -1)
        new_credits = updated_user.credits if updated_user else credits - 1
    except ValueError as e:
        # Jeśli brak kredytów, zwróć odpowiedni komunikat
        return {
            "feedback": str(e),
            "metadata": {
                "credits": credits
            }
        }
    
    # Dodaj zaktualizowaną liczbę kredytów do odpowiedzi
    if "metadata" in response:
        response["metadata"]["credits"] = new_credits
    else:
        response["credits"] = new_credits
    
    return response
