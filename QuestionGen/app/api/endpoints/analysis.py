from fastapi import APIRouter
from app.services.analytics import AnalyticsService

router = APIRouter()

@router.get("/stats/{user_id}")
async def get_user_stats(user_id: str):
    return await AnalyticsService.get_student_stats(user_id)
