from fastapi import APIRouter
from pydantic import BaseModel
from app.services.user_manager import UserService

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str

@router.post("/create")
async def create_user(user: UserCreate):
    return await UserService.create_user(user.username, user.email)

@router.get("/{user_id}")
async def get_user(user_id: str):
    return await UserService.get_user(user_id)
