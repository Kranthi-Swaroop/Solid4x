import os
from bson import ObjectId
from pymongo import MongoClient, ASCENDING

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

client = MongoClient(MONGODB_URI)
db = client["solid4x"]

profiles_col = db["profiles"]
sessions_col = db["sessions"]


# ── Helper ────────────────────────────────────────────────────

def serialize(doc: dict) -> dict:
    """Convert MongoDB _id ObjectId to string for JSON response."""
    if doc is None:
        return {}
    doc = dict(doc)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


# ── Profiles ──────────────────────────────────────────────────

def save_profile(profile: dict) -> str:
    """Upsert by name + exam_date, return inserted/updated _id as string."""
    result = profiles_col.find_one_and_update(
        {"name": profile["name"], "exam_date": profile["exam_date"]},
        {"$set": profile},
        upsert=True,
        return_document=True,
    )
    return str(result["_id"])


# ── Sessions ──────────────────────────────────────────────────

def save_sessions(sessions: list) -> None:
    """Insert all session dicts into the sessions collection."""
    if sessions:
        sessions_col.insert_many(sessions)


def get_sessions(profile_id: str) -> list:
    """Return all sessions for a profile, sorted by date ascending."""
    cursor = sessions_col.find(
        {"profile_id": profile_id}
    ).sort("date", ASCENDING)
    return list(cursor)


def get_missed_sessions(profile_id: str) -> list:
    """Return sessions where status='missed'."""
    cursor = sessions_col.find(
        {"profile_id": profile_id, "status": "missed"}
    ).sort("date", ASCENDING)
    return list(cursor)


def update_session_status(session_id: str, status: str) -> None:
    """Update status field by _id."""
    sessions_col.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"status": status}},
    )
