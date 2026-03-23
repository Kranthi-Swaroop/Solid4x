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
    retention_concepts_col, retention_reviews_col, dashboard_cache_col,
    syllabus_progress_col, study_sessions_col
)
from syllabus_data import get_structured_syllabus, get_total_topic_count

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
# PLANNER — 7-day session plan
# ══════════════════════════════════════════════════════════

def _build_7day_sessions(user_id):
    """Generate a 7-day study session plan ONLY from topics marked weak in syllabus."""
    import random
    from bson import ObjectId

    # Only use topics the user explicitly marked as weak
    syl_doc = syllabus_progress_col().find_one({"user_id": user_id})
    weak = set(syl_doc.get("weak_topics", [])) if syl_doc else set()

    if not weak:
        return []  # nothing selected yet

    syl = get_structured_syllabus()
    topics_pool = []
    for subject, groups in syl.items():
        for g in groups:
            for ch in g["chapters"]:
                for t in ch["topics"]:
                    key = f"{subject}|{ch['chapter']}|{t['name']}"
                    if key in weak:
                        topics_pool.append({
                            "topic": t["name"],
                            "chapter": ch["chapter"],
                            "subject": subject,
                        })

    random.shuffle(topics_pool)
    ordered = topics_pool

    # Get user profile for daily hours
    profile = user_profiles_col().find_one({"user_id": user_id})
    daily_hours = profile.get("daily_hours", 6) if profile else 6
    sessions_per_day = max(3, daily_hours)  # at least 3 sessions per day

    # Spread across 7 days
    today = datetime.utcnow().date()
    sessions = []
    task_types = ["Theory & Notes", "Practice Problems", "Revision", "Problem Solving", "Concept Review"]
    durations = [45, 60, 30, 50, 40]

    for i, t_info in enumerate(ordered[:sessions_per_day * 7]):
        day_offset = i // sessions_per_day
        session_date = today + timedelta(days=day_offset)
        task_type = task_types[i % len(task_types)]
        duration = durations[i % len(durations)]

        sessions.append({
            "_id": ObjectId(),
            "user_id": user_id,
            "topic": t_info["topic"],
            "subject": t_info["subject"],
            "chapter": t_info["chapter"],
            "duration_mins": duration,
            "priority": "high",
            "reason": f"{task_type} — Weak area",
            "status": "pending",
            "date": session_date.isoformat(),
            "created_at": datetime.utcnow().isoformat(),
        })

    return sessions


@app.get("/planner/plan/{user_id}")
def get_plan_sessions(user_id: str):
    """Return 7-day session plan built from syllabus weak topics.
       Auto-regenerates if no pending sessions exist."""
    col = study_sessions_col()
    # Check for pending sessions
    pending = col.count_documents({"user_id": user_id, "status": "pending"})
    if pending == 0:
        # Clear any leftover data and rebuild from current weak topics
        col.delete_many({"user_id": user_id, "status": {"$ne": "done"}})
        sessions = _build_7day_sessions(user_id)
        if sessions:
            col.insert_many(sessions)
    existing = list(col.find({"user_id": user_id}))
    return {"sessions": [_clean(s) for s in existing]}


class SessionStatusRequest(BaseModel):
    status: str  # "done" or "missed"


@app.patch("/planner/session/{session_id}")
def update_session_status(session_id: str, req: SessionStatusRequest):
    """Mark a session as done or missed."""
    from bson import ObjectId
    col = study_sessions_col()
    result = col.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"status": req.status, "completed_at": datetime.utcnow().isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"ok": True}


@app.post("/planner/rebalance/{user_id}")
def rebalance_plan(user_id: str):
    """Delete pending sessions and rebuild the plan, keeping done sessions."""
    col = study_sessions_col()
    # Keep sessions already done
    col.delete_many({"user_id": user_id, "status": {"$ne": "done"}})
    # Rebuild
    new_sessions = _build_7day_sessions(user_id)
    # Filter out topics already done in existing sessions
    done_topics = set()
    for s in col.find({"user_id": user_id, "status": "done"}):
        done_topics.add(f"{s['subject']}|{s['chapter']}|{s['topic']}")
    new_sessions = [s for s in new_sessions if f"{s['subject']}|{s.get('chapter','')}|{s['topic']}" not in done_topics]
    if new_sessions:
        col.insert_many(new_sessions)
    all_sessions = list(col.find({"user_id": user_id}))
    return {"sessions": [_clean(s) for s in all_sessions]}


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
        "syllabus_coverage": get_syllabus_progress(user_id).get("coverage", 0),
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


# ══════════════════════════════════════════════════════════
# SYLLABUS TRACKER
# ══════════════════════════════════════════════════════════

@app.get("/syllabus/full")
def get_full_syllabus():
    """Return the structured JEE syllabus with groups/chapters/topics."""
    from syllabus_data import get_structured_syllabus
    return get_structured_syllabus()


@app.get("/syllabus/progress/{user_id}")
def get_syllabus_progress(user_id: str):
    """Return the user's completed topics and weak topics."""
    doc = syllabus_progress_col().find_one({"user_id": user_id})
    raw_completed = doc.get("completed", []) if doc else []
    raw_weak = doc.get("weak_topics", []) if doc else []
    total = get_total_topic_count()

    # Build set of all valid keys to filter out stale data
    from syllabus_data import get_structured_syllabus
    syl = get_structured_syllabus()
    valid_keys = set()
    for subject, groups in syl.items():
        for g in groups:
            for ch in g["chapters"]:
                for t in ch["topics"]:
                    valid_keys.add(f"{subject}|{ch['chapter']}|{t['name']}")

    completed = [k for k in raw_completed if k in valid_keys]
    weak_topics = [k for k in raw_weak if k in valid_keys]

    # Auto-clean stale keys from DB
    if doc and (len(completed) != len(raw_completed) or len(weak_topics) != len(raw_weak)):
        syllabus_progress_col().update_one(
            {"user_id": user_id},
            {"$set": {"completed": completed, "weak_topics": weak_topics}}
        )

    return {
        "completed": completed,
        "weak_topics": weak_topics,
        "total_topics": total,
        "completed_count": len(completed),
        "coverage": round(len(completed) / total, 4) if total > 0 else 0,
    }


class SyllabusToggleRequest(BaseModel):
    user_id: str
    subject: str
    chapter: str
    topic: str


@app.patch("/syllabus/toggle")
def toggle_syllabus_topic(req: SyllabusToggleRequest):
    """Toggle a topic's completion status."""
    col = syllabus_progress_col()
    key = f"{req.subject}|{req.chapter}|{req.topic}"

    doc = col.find_one({"user_id": req.user_id})
    if not doc:
        col.insert_one({"user_id": req.user_id, "completed": [key], "weak_topics": []})
        completed = [key]
    else:
        completed = doc.get("completed", [])
        if key in completed:
            completed.remove(key)
        else:
            completed.append(key)
        col.update_one(
            {"user_id": req.user_id},
            {"$set": {"completed": completed}}
        )

    total = get_total_topic_count()
    coverage = round(len(completed) / total, 4) if total > 0 else 0

    dashboard_cache_col().update_one(
        {"user_id": req.user_id},
        {"$set": {"syllabus_coverage": coverage, "updated_at": datetime.utcnow().isoformat()}},
        upsert=True
    )
    study_plans_col().update_one(
        {"user_id": req.user_id},
        {"$set": {"syllabus_coverage": coverage}},
        upsert=True
    )

    return {
        "completed": completed,
        "total_topics": total,
        "completed_count": len(completed),
        "coverage": coverage,
    }


class BulkToggleRequest(BaseModel):
    user_id: str
    keys: list[str]       # list of "Subject|Chapter|Topic" keys
    action: str           # "select" or "deselect"


@app.patch("/syllabus/bulk-toggle")
def bulk_toggle_topics(req: BulkToggleRequest):
    """Select or deselect multiple topics at once."""
    col = syllabus_progress_col()
    doc = col.find_one({"user_id": req.user_id})
    if not doc:
        completed = []
        col.insert_one({"user_id": req.user_id, "completed": [], "weak_topics": []})
    else:
        completed = doc.get("completed", [])

    completed_set = set(completed)
    if req.action == "select":
        completed_set.update(req.keys)
    else:
        completed_set -= set(req.keys)

    completed = list(completed_set)
    col.update_one({"user_id": req.user_id}, {"$set": {"completed": completed}})

    total = get_total_topic_count()
    coverage = round(len(completed) / total, 4) if total > 0 else 0

    dashboard_cache_col().update_one(
        {"user_id": req.user_id},
        {"$set": {"syllabus_coverage": coverage, "updated_at": datetime.utcnow().isoformat()}},
        upsert=True
    )
    study_plans_col().update_one(
        {"user_id": req.user_id},
        {"$set": {"syllabus_coverage": coverage}},
        upsert=True
    )

    return {
        "completed": completed,
        "total_topics": total,
        "completed_count": len(completed),
        "coverage": coverage,
    }


class StrengthRequest(BaseModel):
    user_id: str
    subject: str
    chapter: str
    topic: str
    strength: str   # "strong" | "weak" | "none"


@app.patch("/syllabus/set-strength")
def set_topic_strength(req: StrengthRequest):
    """Set a topic as strong, weak, or none (remove)."""
    col = syllabus_progress_col()
    key = f"{req.subject}|{req.chapter}|{req.topic}"

    doc = col.find_one({"user_id": req.user_id})
    if not doc:
        weak = [key] if req.strength == "weak" else []
        col.insert_one({"user_id": req.user_id, "completed": [], "weak_topics": weak})
    else:
        weak = doc.get("weak_topics", [])
        # Remove first, then add if needed
        if key in weak:
            weak.remove(key)
        if req.strength == "weak":
            weak.append(key)
        col.update_one(
            {"user_id": req.user_id},
            {"$set": {"weak_topics": weak}}
        )

    doc = col.find_one({"user_id": req.user_id})
    return {"weak_topics": doc.get("weak_topics", []) if doc else []}


@app.get("/syllabus/weak/{user_id}")
def get_weak_and_incomplete(user_id: str):
    """Return topics explicitly marked weak — includes completed-but-weak topics."""
    doc = syllabus_progress_col().find_one({"user_id": user_id})
    weak = set(doc.get("weak_topics", [])) if doc else set()
    completed = set(doc.get("completed", [])) if doc else set()

    if not weak:
        return {"focus_topics": [], "total": 0}

    from syllabus_data import get_structured_syllabus
    syllabus = get_structured_syllabus()
    focus_topics = []

    for subject, groups in syllabus.items():
        for group in groups:
            for chapter in group["chapters"]:
                for topic in chapter["topics"]:
                    key = f"{subject}|{chapter['chapter']}|{topic['name']}"
                    if key in weak:
                        is_done = key in completed
                        focus_topics.append({
                            "subject": subject,
                            "chapter": chapter["chapter"],
                            "topic": topic["name"],
                            "is_weak": True,
                            "is_incomplete": not is_done,
                            "is_completed": is_done,
                            "priority": "high",
                        })

    # incomplete-weak first, then completed-weak
    focus_topics.sort(key=lambda x: (0 if not x["is_completed"] else 1, x["subject"]))
    return {"focus_topics": focus_topics, "total": len(focus_topics)}

