from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from app.api.dependencies import get_current_user
from app.services.planner_service import PlannerService

router = APIRouter()

class ProfileModel(BaseModel):
    name: str = "Student"
    exam_date: str
    daily_hours: int
    weak_areas: List[str]

class StatusUpdate(BaseModel):
    status: str

@router.post("/onboard")
async def onboard(profile: ProfileModel, user_id: str = Depends(get_current_user)):
    plan = await PlannerService.generate_plan(profile.dict(), user_id)
    return {"user_id": user_id, "plan": plan}

@router.get("/plan")
async def get_plan(user_id: str = Depends(get_current_user)):
    sessions = await PlannerService.get_sessions(user_id)
    return {"sessions": sessions}

@router.patch("/session/{session_id}")
async def update_session(session_id: str, body: StatusUpdate, user_id: str = Depends(get_current_user)):
    await PlannerService.update_session_status(session_id, body.status, user_id)
    return {"message": "Updated"}

@router.post("/rebalance")
async def rebalance(profile: ProfileModel, user_id: str = Depends(get_current_user)):
    plan = await PlannerService.rebalance_plan(profile.dict(), user_id)
    return {"plan": plan}
