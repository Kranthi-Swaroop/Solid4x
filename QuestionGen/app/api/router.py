from fastapi import APIRouter

from app.api.endpoints import practice, repetition, tests, analysis, solver

api_router = APIRouter()

api_router.include_router(practice.router, prefix="/practice", tags=["adaptive practice"])
api_router.include_router(repetition.router, prefix="/repetition", tags=["spaced repetition"])
api_router.include_router(tests.router, prefix="/tests", tags=["test generation"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analytics"])
api_router.include_router(solver.router, prefix="/solver", tags=["concept solver"])
