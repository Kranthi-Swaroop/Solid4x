from fastapi import APIRouter
from pydantic import BaseModel
from app.services.spaced_repetition import SpacedRepetitionService

router = APIRouter()

class ReviewLog(BaseModel):
    user_id: str
    subject: str
    chapter: str
    topic: str
    is_correct: bool

@router.get("/reviews/due/{user_id}")
async def get_due_reviews(user_id: str):
    return await SpacedRepetitionService.get_due_reviews(user_id)

@router.post("/reviews/log")
async def log_review(log: ReviewLog):
    await SpacedRepetitionService.update_knowledge_graph(
        log.user_id, log.subject, log.chapter, log.topic, log.is_correct
    )
    return {"status": "graph updated"}
