from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from .sm2 import sm2
from .database import (upsert_card, get_due_cards, get_all_cards,
                       update_card_after_review, get_knowledge_graph, serialize)

router = APIRouter(prefix="/retention", tags=["retention"])

class CardInput(BaseModel):
    profile_id: str
    topic: str
    subject: str
    source: str = "manual"

class ReviewInput(BaseModel):
    card_id: str
    quality: int           # 0–5

class ProfileQuery(BaseModel):
    profile_id: str

@router.post("/card")
def add_card(card: CardInput):
    card_id = upsert_card(card.profile_id, card.topic, card.subject, card.source)
    return {"card_id": card_id, "message": "Card upserted successfully"}

@router.post("/review")
def review_card(review: ReviewInput):
    from bson import ObjectId
    from .database import cards_col
    
    doc = cards_col.find_one({"_id": ObjectId(review.card_id)})
    if not doc:
        return {"error": "Card not found"}
        
    # Run SM-2
    sm2_result = sm2(review.quality, doc["repetitions"], doc["easiness"], doc["interval"])
    
    # Update logic
    update_card_after_review(review.card_id, sm2_result, review.quality)
    
    # Fetch updated to calculate mastery
    updated_doc = cards_col.find_one({"_id": ObjectId(review.card_id)})
    
    return {
        "updated_card": serialize(updated_doc),
        "next_review_date": sm2_result["next_review_date"],
        "interval": sm2_result["interval"],
        "mastery_score": updated_doc.get("mastery_score", 0)
    }

@router.get("/due/{profile_id}")
def get_due(profile_id: str):
    return get_due_cards(profile_id)

@router.get("/cards/{profile_id}")
def get_cards(profile_id: str):
    return get_all_cards(profile_id)

@router.get("/graph/{profile_id}")
def get_graph(profile_id: str):
    return get_knowledge_graph(profile_id)
