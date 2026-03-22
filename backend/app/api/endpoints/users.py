from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.services.user_manager import UserService
from app.api.dependencies import get_current_user

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

@router.post("/create")
async def create_user(user: UserCreate):
    return await UserService.create_user(user.username, user.email, user.password)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await UserService.authenticate_user(email=form_data.username, password=form_data.password)

@router.get("/me")
async def get_current_user_profile(user_id: str = Depends(get_current_user)):
    return await UserService.get_user(user_id)

@router.get("/{user_id}")
async def get_user(user_id: str):
    return await UserService.get_user(user_id)
