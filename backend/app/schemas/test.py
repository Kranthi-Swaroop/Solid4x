from pydantic import BaseModel
from typing import List, Optional
from app.schemas.question import QuestionResponse

class MockTestRequest(BaseModel):
    user_id: str
    subjects: List[str] = ["Physics", "Chemistry", "Mathematics"]

class MockTestResponse(BaseModel):
    test_id: str
    questions_by_subject: dict[str, List[QuestionResponse]]
    total_questions: int = 75
    section_a_mcq_count: int = 60
    section_b_nvq_count: int = 15

class MockSubmissionItem(BaseModel):
    question_id: str
    is_correct: bool
    time_spent: int
    selected_option: Optional[str] = None

class TestSubmission(BaseModel):
    user_id: str
    test_id: str
    answers: List[MockSubmissionItem]

class TestAnalysisResponse(BaseModel):
    score: int
    weak_areas: dict
    strong_areas: dict
    time_spent_analysis: dict
