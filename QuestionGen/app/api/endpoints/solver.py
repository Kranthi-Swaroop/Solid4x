from fastapi import APIRouter
from app.schemas.solver import ConceptSolverRequest, ConceptSolverResponse
from app.services.concept_solver import ConceptSolverService

router = APIRouter()

@router.post("/solve", response_model=ConceptSolverResponse)
async def solve_concept(request: ConceptSolverRequest):
    return await ConceptSolverService.solve_step_by_step(request.query_text, request.subject)
