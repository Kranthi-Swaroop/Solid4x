from fastapi import APIRouter
from pydantic import BaseModel
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
async def analyze_mock_test(payload: MockSubmissionPayload):
    return await AnalyticsService.process_mock_submission(payload)
