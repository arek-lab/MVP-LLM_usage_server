from fastapi import APIRouter, Depends, Request
from app.auth.utils import get_current_user
from app.services.email.schemas import UserInput, ResponseModel
from app.auth.database import get_user_database
from app.services.email.email_gen_service import generate_email

router = APIRouter()


@router.post("/")
async def email_generator(
    request: Request,
    user_data: UserInput, 
    current_user=Depends(get_current_user)
):
    credits = current_user.credits
    if credits <= 0:
      response = ResponseModel(
        user_query=user_data.email_info,
        output_MD='Liczba kredytów wynosi 0.',
        credtis=credits
        )
      return response
        
    llmResponse = await generate_email(user_data)
    
    # Aktualizacja kredytów
    user_db = get_user_database(request)
    try:
        updated_user = await user_db.increment_credits(current_user.id, -1)
        new_credits = updated_user.credits if updated_user else credits - 1
    except ValueError as e:
        # Jeśli brak kredytów, zwróć odpowiedni komunikat
        return ResponseModel(user_query=user_data.userQuery,
        output_MD=str(e),
        credtis=credits)
            
    
    response = ResponseModel(
      user_query=llmResponse.user_query,
      output_MD=llmResponse.output_MD,
      credtis=new_credits,
      email_title=llmResponse.email_title,
      validation_pass=llmResponse.validation_pass
    )
    
    return response
