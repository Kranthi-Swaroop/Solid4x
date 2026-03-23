from fastapi import APIRouter
from app.api.endpoints import practice, repetition, tests, analysis, solver, users, planner, flashcards, content, syllabus

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["user management"])
api_router.include_router(practice.router, prefix="/practice", tags=["adaptive practice"])
api_router.include_router(repetition.router, prefix="/repetition", tags=["spaced repetition"])
api_router.include_router(tests.router, prefix="/tests", tags=["test generation"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["mock analytics"])
api_router.include_router(solver.router, prefix="/solver", tags=["concept solver"])
api_router.include_router(planner.router, prefix="/planner", tags=["study planner"])
api_router.include_router(flashcards.router, prefix="/flashcards", tags=["retention flashcards"])
api_router.include_router(content.router, prefix="/content", tags=["multimodal video content"])
api_router.include_router(syllabus.router, prefix="/syllabus", tags=["syllabus tracker"])
