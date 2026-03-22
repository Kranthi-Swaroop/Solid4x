import uuid
from datetime import datetime
from app.core.database import get_database
from app.core.config import settings
from fastapi import HTTPException
from app.core.security import get_password_hash, verify_password, create_access_token

class UserService:
    @staticmethod
    async def create_user(username: str, email: str, password: str):
        db = await get_database()
        users = db[settings.MONGODB_DB_NAME]['users']
        
        existing = await users.find_one({"email": email})
        if existing:
            return {"error": "User already exists", "user_id": existing["user_id"]}
            
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(password)
        user_data = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow()
        }
        await users.insert_one(user_data)
        
        return {"status": "success", "user_id": user_id, "username": username}

    @staticmethod
    async def authenticate_user(email: str, password: str):
        db = await get_database()
        users = db[settings.MONGODB_DB_NAME]['users']
        
        user = await users.find_one({"email": email})
        if not user or not verify_password(password, user.get("hashed_password", "")):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
            
        access_token = create_access_token(subject=user["user_id"])
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    async def get_user(user_id: str):
        db = await get_database()
        users = db[settings.MONGODB_DB_NAME]['users']
        
        user = await users.find_one({"user_id": user_id}, {"_id": 0})
        return user or {"error": "User not found"}
