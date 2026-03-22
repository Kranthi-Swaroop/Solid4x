from pydantic import BaseModel, Field
from typing import List, Optional, Any, Union

class QuestionBase(BaseModel):
    subject: str
    chapter: str
    topic: str
    difficulty: str
    question_text: str
    type: Optional[str] = None
    year: Optional[Union[str, int]] = None
    explanation: Optional[str] = None
    is_image_question: bool = False
    options: List[dict] = []
    correct_options: List[str] = []
    answer: Optional[str] = None
    correct_answer: Optional[str] = None

class QuestionResponse(QuestionBase):
    question_id: str

class SimilarQuestionRequest(BaseModel):
    question_id: str
    limit: int = 5
