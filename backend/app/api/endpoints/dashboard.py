from fastapi import APIRouter
from app.core.database import db
from datetime import datetime, timedelta
from app.api.endpoints.syllabus import get_syllabus_progress

router = APIRouter()

def user_profiles_col(): return db.client["solid4x_db"]["user_profiles"]
def study_plans_col(): return db.client["solid4x_db"]["study_plans"]
def dashboard_cache_col(): return db.client["solid4x_db"]["dashboard_cache"]
def retention_concepts_col(): return db.client["solid4x_db"]["retention_concepts"]
def mock_tests_col(): return db.client["solid4x_db"]["mock_tests"]

@router.get("/stats/{user_id}")
async def get_dashboard_stats(user_id: str):
    profile = await user_profiles_col().find_one({"user_id": user_id})
    plan = await study_plans_col().find_one({"user_id": user_id})

    # Dynamically compute the absolute average of all completed mock tests
    completed_tests = await mock_tests_col().find({
        "user_id": user_id, 
        "status": "completed", 
        "score": {"$exists": True}
    }).to_list(length=100)
    
    mock_test_avg = 0
    if completed_tests:
        total_score = sum(float(t.get("score", 0)) for t in completed_tests)
        mock_test_avg = int(round(total_score / len(completed_tests)))

    now = datetime.utcnow()
    due_count = await retention_concepts_col().count_documents({
        "user_id": user_id,
        "next_review": {"$lte": now.isoformat()}
    })

    # Due breakdown by subject
    due_breakdown = {}
    for subject in ["Physics", "Chemistry", "Mathematics"]:
        count = await retention_concepts_col().count_documents({
            "user_id": user_id,
            "subject": subject,
            "next_review": {"$lte": now.isoformat()}
        })
        if count > 0:
            due_breakdown[subject] = count

    today_plan = plan.get("today", []) if plan else []
    done_count = sum(1 for t in today_plan if t.get("done"))
    target_hrs = profile.get("daily_hours", 8) if profile else 8
    completed_hrs = round(done_count * (target_hrs / len(today_plan)), 1) if today_plan else 0

    streak = profile.get("streak_count", 0) if profile else 0
    if profile:
        last_active = profile.get("last_active", "")
        today_str = now.strftime("%Y-%m-%d")
        if last_active and last_active[:10] != today_str:
            yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
            if last_active[:10] == yesterday:
                streak += 1
            else:
                streak = 1
            await user_profiles_col().update_one(
                {"user_id": user_id},
                {"$set": {"streak_count": streak, "last_active": now.isoformat()}}
            )
            
    syl = await get_syllabus_progress(user_id)

    return {
        "student_name": profile.get("name", "Student") if profile else "Student",
        "target_exam": profile.get("target_exam", "JEE Advanced") if profile else "JEE Advanced",
        "exam_date": profile.get("exam_date", "2026-05-24") if profile else "2026-05-24",
        "study_goal": {
            "completed": completed_hrs,
            "target": target_hrs,
        },
        "flashcards_due": due_count,
        "due_breakdown": due_breakdown,
        "mock_test_avg": mock_test_avg,
        "syllabus_coverage": syl.get("coverage", 0),
        "streak": streak,
        "today_plan": today_plan,
        "onboarding_completed": profile.get("onboarding_completed", False) if profile else False,
    }
