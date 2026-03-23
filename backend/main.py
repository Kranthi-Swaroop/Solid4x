"""
Solid4x Backend — FastAPI server for planner, retention, and dashboard.
Run: cd backend && python -m uvicorn main:app --reload --port 8001
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import math

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from database import (
    user_profiles_col, study_plans_col,
    retention_concepts_col, retention_reviews_col, dashboard_cache_col
)

app = FastAPI(title="Solid4x Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ══════════════════════════════════════════════════════════
# TOPIC CONSTANTS — shared by onboarding + retention picker
# ══════════════════════════════════════════════════════════

ALL_TOPICS = {
    "Physics": [
        "Mechanics", "Thermodynamics", "Electrostatics", "Optics",
        "Modern Physics", "Waves", "Magnetism", "Current Electricity",
        "Gravitation", "Rotational Motion", "Fluid Mechanics",
    ],
    "Chemistry": [
        "Mole Concept", "Electrochemistry", "Organic Reactions", "Equilibrium",
        "Coordination Chemistry", "Thermochemistry", "Chemical Bonding",
        "Periodic Table", "Solutions", "Chemical Kinetics", "Polymers",
    ],
    "Mathematics": [
        "Calculus", "Algebra", "Coordinate Geometry", "Trigonometry",
        "Vectors", "Probability", "Matrices", "Differential Equations",
        "Complex Numbers", "Permutations & Combinations", "Statistics",
    ],
}


# ══════════════════════════════════════════════════════════
# ONBOARDING
# ══════════════════════════════════════════════════════════

class OnboardingRequest(BaseModel):
    user_id: str
    name: str
    exam_date: str
    daily_hours: int = 6
    weak_areas: list[str] = []
    target_exam: str = "JEE Advanced"


@app.post("/planner/onboard")
def onboard(req: OnboardingRequest):
    """Create user profile + initial study plan + retention concepts for weak areas."""
    profiles = user_profiles_col()
    plans = study_plans_col()
    concepts = retention_concepts_col()

    # Check if already onboarded
    existing = profiles.find_one({"user_id": req.user_id})
    if existing:
        return {
            "profile_id": req.user_id,
            "message": "Already onboarded",
            "onboarding_completed": True,
        }

    # 1. Create user profile
    profile_doc = {
        "user_id": req.user_id,
        "name": req.name,
        "exam_date": req.exam_date,
        "daily_hours": req.daily_hours,
        "target_exam": req.target_exam,
        "weak_areas": req.weak_areas,
        "onboarding_completed": True,
        "streak_count": 0,
        "last_active": datetime.utcnow().isoformat(),
        "created_at": datetime.utcnow().isoformat(),
    }
    profiles.insert_one(profile_doc)

    # 2. Generate initial study plan
    today_plan = _generate_daily_plan(req.weak_areas, req.daily_hours)
    plan_doc = {
        "user_id": req.user_id,
        "today": today_plan,
        "syllabus_coverage": 0.0,
        "created_at": datetime.utcnow().isoformat(),
        "last_rebalanced": datetime.utcnow().isoformat(),
    }
    plans.insert_one(plan_doc)

    # 3. Create retention concepts for weak areas
    now = datetime.utcnow()
    for topic in req.weak_areas:
        subject = _find_subject_for_topic(topic)
        concepts.insert_one({
            "user_id": req.user_id,
            "topic": topic,
            "subject": subject,
            "mastery_score": 0.0,
            "easiness": 2.5,
            "interval": 1,
            "repetitions": 0,
            "next_review": now.isoformat(),
            "last_reviewed": None,
            "source": "onboarding",
        })

    # 4. Init dashboard cache
    dashboard_cache_col().update_one(
        {"user_id": req.user_id},
        {"$set": {
            "user_id": req.user_id,
            "study_goal_completed": 0,
            "study_goal_target": req.daily_hours,
            "flashcards_due": len(req.weak_areas),
            "mock_test_avg": 0,
            "syllabus_coverage": 0,
            "streak": 0,
            "updated_at": now.isoformat(),
        }},
        upsert=True
    )

    return {
        "profile_id": req.user_id,
        "message": "Onboarding complete",
        "onboarding_completed": True,
        "plan": today_plan,
    }


# ══════════════════════════════════════════════════════════
# ONBOARDING STATUS CHECK
# ══════════════════════════════════════════════════════════

@app.get("/planner/onboarding-status/{user_id}")
def onboarding_status(user_id: str):
    profile = user_profiles_col().find_one({"user_id": user_id})
    if profile and profile.get("onboarding_completed"):
        return {"onboarding_completed": True, "profile": _clean(profile)}
    return {"onboarding_completed": False}


# ══════════════════════════════════════════════════════════
# PLANNER — Today's plan
# ══════════════════════════════════════════════════════════

@app.get("/planner/today/{user_id}")
def get_today_plan(user_id: str):
    plan = study_plans_col().find_one({"user_id": user_id})
    if not plan:
        raise HTTPException(status_code=404, detail="No plan found. Complete onboarding first.")
    return {
        "today": plan.get("today", []),
        "syllabus_coverage": plan.get("syllabus_coverage", 0),
    }


class TaskDoneRequest(BaseModel):
    task_index: int
    done: bool = True


@app.patch("/planner/today/{user_id}/task")
def mark_task_done(user_id: str, req: TaskDoneRequest):
    plans = study_plans_col()
    plan = plans.find_one({"user_id": user_id})
    if not plan:
        raise HTTPException(status_code=404, detail="No plan found")

    today = plan.get("today", [])
    if 0 <= req.task_index < len(today):
        today[req.task_index]["done"] = req.done
        # recalc coverage
        done_count = sum(1 for t in today if t.get("done"))
        coverage = done_count / len(today) if today else 0
        plans.update_one(
            {"user_id": user_id},
            {"$set": {"today": today, "syllabus_coverage": round(coverage, 2)}}
        )
        # update dashboard cache
        profile = user_profiles_col().find_one({"user_id": user_id})
        target_hrs = profile.get("daily_hours", 8) if profile else 8
        completed_hrs = round(done_count * (target_hrs / len(today)), 1) if today else 0
        dashboard_cache_col().update_one(
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


# ══════════════════════════════════════════════════════════
# RETENTION — Due cards, graph, add/review
# ══════════════════════════════════════════════════════════

@app.get("/retention/topics-list")
def get_topics_list():
    """Return all available topics grouped by subject for the topic picker."""
    return ALL_TOPICS


@app.get("/retention/due/{user_id}")
def get_due_cards(user_id: str):
    now = datetime.utcnow().isoformat()
    concepts = retention_concepts_col()
    due = list(concepts.find(
        {"user_id": user_id, "next_review": {"$lte": now}},
    ))
    return [_clean(c) for c in due]


@app.get("/retention/graph/{user_id}")
def get_knowledge_graph(user_id: str):
    concepts = retention_concepts_col()
    all_concepts = list(concepts.find({"user_id": user_id}))

    graph = {}
    for subject in ["Physics", "Chemistry", "Mathematics"]:
        subject_concepts = [c for c in all_concepts if c.get("subject") == subject]
        total = len(subject_concepts)
        mastered = sum(1 for c in subject_concepts if c.get("mastery_score", 0) >= 4)
        due = sum(1 for c in subject_concepts if c.get("next_review", "") <= datetime.utcnow().isoformat())
        topics = []
        for c in subject_concepts:
            topics.append({
                "concept_id": str(c["_id"]),
                "topic": c["topic"],
                "mastery_score": c.get("mastery_score", 0),
                "easiness": c.get("easiness", 2.5),
                "interval": c.get("interval", 1),
                "repetitions": c.get("repetitions", 0),
                "next_review": c.get("next_review", ""),
            })
        graph[subject] = {"total": total, "mastered": mastered, "due": due, "topics": topics}

    return graph


class AddConceptRequest(BaseModel):
    profile_id: str
    topic: str
    subject: str
    source: str = "manual"


@app.post("/retention/card")
def add_concept(req: AddConceptRequest):
    concepts = retention_concepts_col()
    existing = concepts.find_one({"user_id": req.profile_id, "topic": req.topic, "subject": req.subject})
    if existing:
        return {"ok": True, "message": "Topic already exists"}

    now = datetime.utcnow()
    concepts.insert_one({
        "user_id": req.profile_id,
        "topic": req.topic,
        "subject": req.subject,
        "mastery_score": 0.0,
        "easiness": 2.5,
        "interval": 1,
        "repetitions": 0,
        "next_review": now.isoformat(),
        "last_reviewed": None,
        "source": req.source,
    })
    _refresh_due_count(req.profile_id)
    return {"ok": True}


class BulkAddRequest(BaseModel):
    user_id: str
    topics: list[dict]  # [{"topic": "...", "subject": "..."}]


@app.post("/retention/add-topics")
def bulk_add_topics(req: BulkAddRequest):
    concepts = retention_concepts_col()
    now = datetime.utcnow()
    added = 0
    for item in req.topics:
        existing = concepts.find_one({
            "user_id": req.user_id,
            "topic": item["topic"],
            "subject": item["subject"]
        })
        if not existing:
            concepts.insert_one({
                "user_id": req.user_id,
                "topic": item["topic"],
                "subject": item["subject"],
                "mastery_score": 0.0,
                "easiness": 2.5,
                "interval": 1,
                "repetitions": 0,
                "next_review": now.isoformat(),
                "last_reviewed": None,
                "source": "picker",
            })
            added += 1
    _refresh_due_count(req.user_id)
    return {"ok": True, "added": added}


class ReviewRequest(BaseModel):
    profile_id: str
    concept_id: str
    quality: int  # 0-5 SM-2 quality


@app.post("/retention/review")
def review_concept(req: ReviewRequest):
    from bson import ObjectId
    concepts = retention_concepts_col()
    reviews = retention_reviews_col()

    concept = concepts.find_one({"_id": ObjectId(req.concept_id)})
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    # SM-2 algorithm
    q = req.quality
    ef = concept.get("easiness", 2.5)
    interval = concept.get("interval", 1)
    reps = concept.get("repetitions", 0)

    if q >= 3:
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 6
        else:
            interval = math.ceil(interval * ef)
        reps += 1
    else:
        reps = 0
        interval = 1

    ef = max(1.3, ef + 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    mastery = min(5.0, (q / 5.0) * 5 * (1 - 1 / (reps + 1)) + concept.get("mastery_score", 0) * (1 / (reps + 1)))

    now = datetime.utcnow()
    next_review = now + timedelta(days=interval)

    concepts.update_one(
        {"_id": ObjectId(req.concept_id)},
        {"$set": {
            "easiness": round(ef, 2),
            "interval": interval,
            "repetitions": reps,
            "mastery_score": round(mastery, 2),
            "next_review": next_review.isoformat(),
            "last_reviewed": now.isoformat(),
        }}
    )

    reviews.insert_one({
        "user_id": req.profile_id,
        "concept_id": req.concept_id,
        "quality": q,
        "reviewed_at": now.isoformat(),
    })

    _refresh_due_count(req.profile_id)

    return {
        "ok": True,
        "new_interval": interval,
        "new_easiness": round(ef, 2),
        "mastery_score": round(mastery, 2),
        "next_review": next_review.isoformat(),
    }


# ══════════════════════════════════════════════════════════
# DASHBOARD STATS
# ══════════════════════════════════════════════════════════

@app.get("/dashboard/stats/{user_id}")
def get_dashboard_stats(user_id: str):
    profile = user_profiles_col().find_one({"user_id": user_id})
    cache = dashboard_cache_col().find_one({"user_id": user_id})
    plan = study_plans_col().find_one({"user_id": user_id})

    now = datetime.utcnow()
    due_count = retention_concepts_col().count_documents({
        "user_id": user_id,
        "next_review": {"$lte": now.isoformat()}
    })

    # Due breakdown by subject
    due_breakdown = {}
    for subject in ["Physics", "Chemistry", "Mathematics"]:
        count = retention_concepts_col().count_documents({
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

    # Calculate streak
    streak = profile.get("streak_count", 0) if profile else 0
    # Update last_active and streak
    if profile:
        last_active = profile.get("last_active", "")
        today_str = now.strftime("%Y-%m-%d")
        if last_active and last_active[:10] != today_str:
            yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
            if last_active[:10] == yesterday:
                streak += 1
            else:
                streak = 1
            user_profiles_col().update_one(
                {"user_id": user_id},
                {"$set": {"streak_count": streak, "last_active": now.isoformat()}}
            )

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
        "mock_test_avg": cache.get("mock_test_avg", 0) if cache else 0,
        "syllabus_coverage": plan.get("syllabus_coverage", 0) if plan else 0,
        "streak": streak,
        "today_plan": today_plan,
        "onboarding_completed": profile.get("onboarding_completed", False) if profile else False,
    }


# ══════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════

def _clean(doc):
    """Remove MongoDB _id for JSON serialization."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def _find_subject_for_topic(topic):
    for subject, topics in ALL_TOPICS.items():
        if topic in topics:
            return subject
    return "Physics"


def _generate_daily_plan(weak_areas, daily_hours):
    """Generate a study plan based on weak areas and available hours."""
    plan = []
    hours = ["08:00", "09:30", "11:00", "12:30", "14:00", "15:30", "17:00", "18:30", "20:00"]
    task_types = ["theory", "practice", "revision", "problems"]

    # Mix weak areas with balanced coverage
    all_subjects = list(ALL_TOPICS.keys())
    tasks_count = min(daily_hours, len(hours))

    for i in range(tasks_count):
        if i < len(weak_areas):
            topic = weak_areas[i]
            subject = _find_subject_for_topic(topic)
        else:
            subject = all_subjects[i % len(all_subjects)]
            subject_topics = ALL_TOPICS[subject]
            topic = subject_topics[i % len(subject_topics)]

        plan.append({
            "time": hours[i] if i < len(hours) else f"{8 + i}:00",
            "subject": subject,
            "topic": topic,
            "type": task_types[i % len(task_types)],
            "done": False,
        })

    return plan


def _refresh_due_count(user_id):
    """Update the flashcards_due count in dashboard cache."""
    now = datetime.utcnow()
    due_count = retention_concepts_col().count_documents({
        "user_id": user_id,
        "next_review": {"$lte": now.isoformat()}
    })
    dashboard_cache_col().update_one(
        {"user_id": user_id},
        {"$set": {"flashcards_due": due_count, "updated_at": now.isoformat()}},
        upsert=True
    )
