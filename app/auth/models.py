from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class User(BaseModel):
    id: str
    email: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime
    


class UserInDB(User):
    credits: int
