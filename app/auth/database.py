import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import Request
from passlib.context import CryptContext
from app.auth.models import UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserDatabase:
    def __init__(self, request: Request = None):
        self.request = request

    @property
    def collection(self):
        """Get users collection from FastAPI app"""
        if not self.request:
            raise ValueError("Request object is required to access database")
        return self.request.app.mongodb.users

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        user_data = await self.collection.find_one({"email": email})
        if user_data:
            # Convert MongoDB's _id to id
            user_data["id"] = user_data.pop("_id")
            return UserInDB(**user_data)
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        user_data = await self.collection.find_one({"_id": user_id})
        if user_data:
            # Convert MongoDB's _id to id
            user_data["id"] = user_data.pop("_id")
            return UserInDB(**user_data)
        return None

    async def create_user(self, email: str, password: str) -> UserInDB:
        # Check if user already exists
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise ValueError("User already exists")

        user_id = str(uuid.uuid4())
        hashed_password = self.get_password_hash(password)

        user_data = {
            "_id": user_id,
            "email": email,
            "hashed_password": hashed_password,
            "is_active": False,
            "credits": 100,
            "created_at": datetime.now(timezone.utc),
        }

        await self.collection.insert_one(user_data)

        # Convert _id to id for return value
        user_data["id"] = user_data.pop("_id")
        return UserInDB(**user_data)

    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    async def update_credits(self, user_id: str, credits: int) -> Optional[UserInDB]:
        """Update user's credits"""
        if credits < 0:
            raise ValueError("Credits cannot be negative")
        
        result = await self.collection.find_one_and_update(
            {"_id": user_id},
            {"$set": {"credits": credits}},
            return_document=True
        )
        
        if result:
            result["id"] = result.pop("_id")
            return UserInDB(**result)
        return None

    async def increment_credits(self, user_id: str, amount: int) -> Optional[UserInDB]:
        """Increment or decrement user's credits by amount (use negative for decrement)"""
        # First get current credits to validate
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        new_credits = user.credits + amount
        if new_credits < 0:
            raise ValueError("Insufficient credits. Operation would result in negative balance")
        
        result = await self.collection.find_one_and_update(
            {"_id": user_id},
            {"$inc": {"credits": amount}},
            return_document=True
        )
        
        if result:
            result["id"] = result.pop("_id")
            return UserInDB(**result)
        return None


# Dependency function to get UserDatabase instance
def get_user_database(request: Request) -> UserDatabase:
    return UserDatabase(request)
