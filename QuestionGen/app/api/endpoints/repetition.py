from fastapi import APIRouter
from app.services.spaced_repetition import SpacedRepetitionService

router = APIRouter()

@router.get("/reviews/due/{user_id}")
async def get_due_reviews(user_id: str):
    return await SpacedRepetitionService.get_due_reviews(user_id)
