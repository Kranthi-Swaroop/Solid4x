from fastapi import APIRouter
from pydantic import BaseModel
from app.services.concept_solver import ConceptSolverService

router = APIRouter()

class SolverRequest(BaseModel):
    question_id: str

@router.post("/explain")
async def explain_concept(request: SolverRequest):
    return await ConceptSolverService.solve_question(request.question_id)
