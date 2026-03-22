from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.dependencies import get_current_user
from typing import List
from app.services.analytics import AnalyticsService

router = APIRouter()

class MockSubmissionItem(BaseModel):
    question_id: str
    is_correct: bool
    time_spent: int

class MockSubmissionPayload(BaseModel):
    user_id: str
    test_id: str
    answers: List[MockSubmissionItem]

@router.post("/mock")
async def analyze_mock_test(payload: MockSubmissionPayload, user_id: str = Depends(get_current_user)):
    return await AnalyticsService.process_mock_submission(payload)
