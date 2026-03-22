from fastapi import APIRouter
from app.schemas.test import MockTestRequest, MockTestResponse, TestSubmission, TestAnalysisResponse
from app.services.test_generator import TestGeneratorService

router = APIRouter()

@router.post("/generate", response_model=MockTestResponse)
async def generate_mock_test(request: MockTestRequest):
    return await TestGeneratorService.generate_mock_test(request.user_id, request.subjects)

@router.post("/submit", response_model=TestAnalysisResponse)
async def submit_test(submission: TestSubmission):
    return await TestGeneratorService.analyze_submission(
        submission.user_id, submission.test_id, submission.answers
    )

@router.get("/history/{user_id}")
async def get_user_mock_tests(user_id: str):
    return await TestGeneratorService.get_user_mock_tests(user_id)
