from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from .planner import generate_plan, rebalance_plan
from .database import save_profile, get_sessions, update_session_status, serialize

router = APIRouter(prefix="/planner", tags=["planner"])


class ProfileModel(BaseModel):
    name: str
    exam_date: str
    daily_hours: int
    weak_areas: List[str]


class StatusUpdate(BaseModel):
    status: str


@router.post("/onboard")
def onboard(profile: ProfileModel):
    profile_id = save_profile(profile.dict())
    plan = generate_plan(profile.dict(), profile_id)
    return {"profile_id": profile_id, "plan": plan}


@router.get("/plan/{profile_id}")
def get_plan(profile_id: str):
    sessions = get_sessions(profile_id)
    return {"sessions": [serialize(s) for s in sessions]}


@router.patch("/session/{session_id}")
def update_session(session_id: str, body: StatusUpdate):
    update_session_status(session_id, body.status)
    return {"message": "Updated"}


@router.post("/rebalance/{profile_id}")
def rebalance(profile_id: str, profile: ProfileModel):
    plan = rebalance_plan(profile.dict(), profile_id)
    return {"plan": plan}
