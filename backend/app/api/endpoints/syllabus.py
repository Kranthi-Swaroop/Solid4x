"""
Syllabus Tracker endpoints — integrated into the main app.
Uses motor (async) to match the existing app database layer.
"""
import sys
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

# Make sure we can import syllabus_data from the backend root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from syllabus_data import get_structured_syllabus, get_total_topic_count

from app.core.database import db
from app.core.config import settings

router = APIRouter()

DB_NAME = settings.MONGODB_DB_NAME


def _syllabus_progress_col():
    return db.client[DB_NAME]["syllabus_progress"]


def _dashboard_cache_col():
    return db.client[DB_NAME]["dashboard_cache"]


def _study_plans_col():
    return db.client[DB_NAME]["study_plans"]


# ── GET full syllabus ──
@router.get("/full")
async def get_full_syllabus():
    """Return the structured JEE syllabus with groups/chapters/topics."""
    return get_structured_syllabus()


# ── GET progress ──
@router.get("/progress/{user_id}")
async def get_syllabus_progress(user_id: str):
    """Return the user's completed topics and weak topics."""
    col = _syllabus_progress_col()
    doc = await col.find_one({"user_id": user_id})
    raw_completed = doc.get("completed", []) if doc else []
    raw_weak = doc.get("weak_topics", []) if doc else []
    total = get_total_topic_count()

    # Build valid keys to filter stale data
    syl = get_structured_syllabus()
    valid_keys = set()
    for subject, groups in syl.items():
        for g in groups:
            for ch in g["chapters"]:
                for t in ch["topics"]:
                    valid_keys.add(f"{subject}|{ch['chapter']}|{t['name']}")

    completed = [k for k in raw_completed if k in valid_keys]
    weak_topics = [k for k in raw_weak if k in valid_keys]

    # Auto-clean stale keys
    if doc and (len(completed) != len(raw_completed) or len(weak_topics) != len(raw_weak)):
        await col.update_one(
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


# ── PATCH toggle topic ──
class SyllabusToggleRequest(BaseModel):
    user_id: str
    subject: str
    chapter: str
    topic: str


@router.patch("/toggle")
async def toggle_syllabus_topic(req: SyllabusToggleRequest):
    """Toggle a topic's completion status."""
    col = _syllabus_progress_col()
    key = f"{req.subject}|{req.chapter}|{req.topic}"

    doc = await col.find_one({"user_id": req.user_id})
    if not doc:
        await col.insert_one({"user_id": req.user_id, "completed": [key], "weak_topics": []})
        completed = [key]
    else:
        completed = doc.get("completed", [])
        if key in completed:
            completed.remove(key)
        else:
            completed.append(key)
        await col.update_one(
            {"user_id": req.user_id},
            {"$set": {"completed": completed}}
        )

    total = get_total_topic_count()
    coverage = round(len(completed) / total, 4) if total > 0 else 0

    await _dashboard_cache_col().update_one(
        {"user_id": req.user_id},
        {"$set": {"syllabus_coverage": coverage}},
        upsert=True
    )
    await _study_plans_col().update_one(
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


# ── PATCH bulk-toggle ──
class BulkToggleRequest(BaseModel):
    user_id: str
    keys: List[str]
    action: str  # "select" or "deselect"


@router.patch("/bulk-toggle")
async def bulk_toggle_topics(req: BulkToggleRequest):
    """Select or deselect multiple topics at once."""
    col = _syllabus_progress_col()
    doc = await col.find_one({"user_id": req.user_id})
    if not doc:
        completed = []
        await col.insert_one({"user_id": req.user_id, "completed": [], "weak_topics": []})
    else:
        completed = doc.get("completed", [])

    completed_set = set(completed)
    if req.action == "select":
        completed_set.update(req.keys)
    else:
        completed_set -= set(req.keys)

    completed = list(completed_set)
    await col.update_one({"user_id": req.user_id}, {"$set": {"completed": completed}})

    total = get_total_topic_count()
    coverage = round(len(completed) / total, 4) if total > 0 else 0

    await _dashboard_cache_col().update_one(
        {"user_id": req.user_id},
        {"$set": {"syllabus_coverage": coverage}},
        upsert=True
    )
    await _study_plans_col().update_one(
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


# ── PATCH set-strength ──
class StrengthRequest(BaseModel):
    user_id: str
    subject: str
    chapter: str
    topic: str
    strength: str  # "strong" | "weak" | "none"


@router.patch("/set-strength")
async def set_topic_strength(req: StrengthRequest):
    """Set a topic as strong, weak, or none."""
    col = _syllabus_progress_col()
    key = f"{req.subject}|{req.chapter}|{req.topic}"

    doc = await col.find_one({"user_id": req.user_id})
    if not doc:
        weak = [key] if req.strength == "weak" else []
        await col.insert_one({"user_id": req.user_id, "completed": [], "weak_topics": weak})
    else:
        weak = doc.get("weak_topics", [])
        if key in weak:
            weak.remove(key)
        if req.strength == "weak":
            weak.append(key)
        await col.update_one(
            {"user_id": req.user_id},
            {"$set": {"weak_topics": weak}}
        )

    doc = await col.find_one({"user_id": req.user_id})
    return {"weak_topics": doc.get("weak_topics", []) if doc else []}


# ── GET weak topics ──
@router.get("/weak/{user_id}")
async def get_weak_and_incomplete(user_id: str):
    """Return topics explicitly marked weak."""
    col = _syllabus_progress_col()
    doc = await col.find_one({"user_id": user_id})
    weak = set(doc.get("weak_topics", [])) if doc else set()
    completed_set = set(doc.get("completed", [])) if doc else set()

    if not weak:
        return {"focus_topics": [], "total": 0}

    syllabus = get_structured_syllabus()
    focus_topics = []

    for subject, groups in syllabus.items():
        for group in groups:
            for chapter in group["chapters"]:
                for topic in chapter["topics"]:
                    key = f"{subject}|{chapter['chapter']}|{topic['name']}"
                    if key in weak:
                        is_done = key in completed_set
                        focus_topics.append({
                            "subject": subject,
                            "chapter": chapter["chapter"],
                            "topic": topic["name"],
                            "is_weak": True,
                            "is_incomplete": not is_done,
                            "is_completed": is_done,
                            "priority": "high",
                        })

    focus_topics.sort(key=lambda x: (0 if not x["is_completed"] else 1, x["subject"]))
    return {"focus_topics": focus_topics, "total": len(focus_topics)}
