from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.dependencies import get_current_user
from app.services.retention_sm2 import RetentionService

router = APIRouter()

class CardInput(BaseModel):
    topic: str
    subject: str
    source: str = "manual"

class ReviewInput(BaseModel):
    card_id: str
    quality: int

@router.post("/card")
async def add_card(card: CardInput, user_id: str = Depends(get_current_user)):
    card_id = await RetentionService.upsert_card(user_id, card.topic, card.subject, card.source)
    return {"card_id": card_id, "message": "Card upserted successfully"}

@router.post("/review")
async def review_card(review: ReviewInput, user_id: str = Depends(get_current_user)):
    return await RetentionService.process_review(review.card_id, review.quality)

@router.get("/due")
async def get_due_cards(user_id: str = Depends(get_current_user)):
    return await RetentionService.get_due_cards(user_id)

@router.get("/cards")
async def get_cards(user_id: str = Depends(get_current_user)):
    return await RetentionService.get_all_cards(user_id)

@router.get("/graph")
async def get_graph(user_id: str = Depends(get_current_user)):
    return await RetentionService.get_knowledge_graph(user_id)
