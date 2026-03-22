from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.question import SimilarQuestionRequest, QuestionResponse
from app.services.adaptive_practice import AdaptivePracticeService

router = APIRouter()

class PracticeSubmission(BaseModel):
    user_id: str
    question_id: str
    is_correct: bool
    time_spent: int

@router.post("/similar", response_model=list[QuestionResponse])
async def get_similar_questions(request: SimilarQuestionRequest):
    return await AdaptivePracticeService.get_similar_questions(request.question_id, request.limit)

@router.get("/generate", response_model=list[QuestionResponse])
async def generate_practice_questions(user_id: str, chapter: str = None, topic: str = None, limit: int = 5):
    return await AdaptivePracticeService.generate_practice_questions(user_id, chapter, topic, limit)

@router.post("/submit")
async def submit_practice_answer(submission: PracticeSubmission):
    await AdaptivePracticeService.analyze_error_rates(
        submission.user_id, submission.question_id, submission.is_correct, submission.time_spent
    )
    return {"status": "logged successfully"}
