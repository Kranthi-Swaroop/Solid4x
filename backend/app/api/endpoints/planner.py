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


# ══════════════════════════════════════════════════════════
# LEGACY UN-AUTHENTICATED ROUTES (FRONTEND MIGRATION)
# ══════════════════════════════════════════════════════════

from app.core.database import db
from datetime import datetime
from fastapi import HTTPException

def user_profiles_col(): return db.client["solid4x_db"]["user_profiles"]
def study_plans_col(): return db.client["solid4x_db"]["study_plans"]
def dashboard_cache_col(): return db.client["solid4x_db"]["dashboard_cache"]

def _clean(doc):
    if doc and "_id" in doc: doc["_id"] = str(doc["_id"])
    return doc

@router.get("/onboarding-status/{user_id}")
async def onboarding_status(user_id: str):
    profile = await user_profiles_col().find_one({"user_id": user_id})
    if profile and profile.get("onboarding_completed"):
        return {"onboarding_completed": True, "profile": _clean(profile)}
    return {"onboarding_completed": False}

@router.get("/today/{user_id}")
async def get_today_plan(user_id: str):
    plan = await study_plans_col().find_one({"user_id": user_id})
    if not plan:
        raise HTTPException(status_code=404, detail="No plan found. Complete onboarding first.")
    return {
        "today": plan.get("today", []),
        "syllabus_coverage": plan.get("syllabus_coverage", 0),
    }

class TaskDoneRequest(BaseModel):
    task_index: int
    done: bool = True

@router.patch("/today/{user_id}/task")
async def mark_task_done(user_id: str, req: TaskDoneRequest):
    plans = study_plans_col()
    plan = await plans.find_one({"user_id": user_id})
    if not plan:
        raise HTTPException(status_code=404, detail="No plan found")

    today = plan.get("today", [])
    if 0 <= req.task_index < len(today):
        today[req.task_index]["done"] = req.done
        done_count = sum(1 for t in today if t.get("done"))
        coverage = done_count / len(today) if today else 0
        await plans.update_one(
            {"user_id": user_id},
            {"$set": {"today": today, "syllabus_coverage": round(coverage, 2)}}
        )
        profile = await user_profiles_col().find_one({"user_id": user_id})
        target_hrs = profile.get("daily_hours", 8) if profile else 8
        completed_hrs = round(done_count * (target_hrs / len(today)), 1) if today else 0
        await dashboard_cache_col().update_one(
            {"user_id": user_id},
            {"$set": {
                "study_goal_completed": completed_hrs,
                "study_goal_target": target_hrs,
                "syllabus_coverage": round(coverage, 2),
                "updated_at": datetime.utcnow().isoformat(),
            }},
            upsert=True
        )
        return {"ok": True, "today": today}
    raise HTTPException(status_code=400, detail="Invalid task index")
