from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request

from app.config import settings
from app.auth.schemas import UserCreate, UserLogin, UserResponse, Token
from app.auth.database import get_user_database, UserDatabase
from app.auth.utils import get_current_user, create_access_token

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    request: Request,
    user_db: UserDatabase = Depends(get_user_database),
):
    # Set request for database access
    user_db.request = request

    try:
        user = await user_db.create_user(user_data.email, user_data.password)
        return UserResponse(id=user.id, email=user.email, is_active=user.is_active)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    request: Request,
    user_db: UserDatabase = Depends(get_user_database),
):
    # Set request for database access
    user_db.request = request
    user = await user_db.authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not active. Please contact administrator.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user=Depends(get_current_user)):
    return UserResponse(
        id=current_user.id, email=current_user.email, is_active=current_user.is_active
    )
