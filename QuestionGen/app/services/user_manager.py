import uuid
from datetime import datetime
from app.core.database import get_database
from app.core.config import settings

class UserService:
    @staticmethod
    async def create_user(username: str, email: str):
        db = await get_database()
        users = db[settings.MONGODB_DB_NAME]['users']
        
        existing = await users.find_one({"email": email})
        if existing:
            return {"error": "User already exists", "user_id": existing["user_id"]}
            
        user_id = str(uuid.uuid4())
        user_data = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "created_at": datetime.utcnow()
        }
        await users.insert_one(user_data)
        
        return {"status": "success", "user_id": user_id, "username": username}

    @staticmethod
    async def get_user(user_id: str):
        db = await get_database()
        users = db[settings.MONGODB_DB_NAME]['users']
        
        user = await users.find_one({"user_id": user_id}, {"_id": 0})
        return user or {"error": "User not found"}
