from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.dependencies import get_current_user
from app.services.concept_solver import ConceptSolverService

router = APIRouter()

class SolverRequest(BaseModel):
    question_id: str

@router.post("/explain")
async def explain_concept(request: SolverRequest, user_id: str = Depends(get_current_user)):
    return await ConceptSolverService.solve_question(request.question_id)
