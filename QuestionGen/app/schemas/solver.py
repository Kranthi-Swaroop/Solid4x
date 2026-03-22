from pydantic import BaseModel

class ConceptSolverRequest(BaseModel):
    query_text: str
    subject: str # e.g., Calculus, Organic Chemistry

class ConceptSolverResponse(BaseModel):
    steps: list[str]
    final_answer: str
