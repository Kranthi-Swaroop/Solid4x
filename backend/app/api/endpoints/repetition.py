from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.dependencies import get_current_user
from app.services.spaced_repetition import SpacedRepetitionService

router = APIRouter()

class ReviewLog(BaseModel):
    user_id: str
    subject: str
    chapter: str
    topic: str
    is_correct: bool

@router.get("/reviews/due")
async def get_due_reviews(user_id: str = Depends(get_current_user)):
    return await SpacedRepetitionService.get_due_reviews(user_id)

@router.post("/reviews/log")
async def log_review(log: ReviewLog, user_id: str = Depends(get_current_user)):
    await SpacedRepetitionService.update_knowledge_graph(
        log.user_id, log.subject, log.chapter, log.topic, log.is_correct
    )
    return {"status": "graph updated"}

@router.get("/unpracticed")
async def get_unpracticed_topics(subject: str, user_id: str = Depends(get_current_user)):
    topics = await SpacedRepetitionService.get_unpracticed_topics(user_id, subject)
    return {"unpracticed_topics": topics}

@router.get("/topics/status")
async def get_topics_status(user_id: str = Depends(get_current_user)):
    return await SpacedRepetitionService.get_topics_status(user_id)

