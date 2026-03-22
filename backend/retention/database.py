import os
from datetime import datetime, date
from pymongo import MongoClient, ASCENDING
from bson import ObjectId

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(MONGODB_URI)
db = client["solid4x"]
cards_col = db["concept_cards"]

# Indexes for faster query
cards_col.create_index([("profile_id", ASCENDING), ("topic", ASCENDING)])
cards_col.create_index([("profile_id", ASCENDING), ("next_review_date", ASCENDING)])

def serialize(doc: dict) -> dict:
    if not doc:
        return {}
    doc = dict(doc)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

def upsert_card(profile_id: str, topic: str, subject: str, source: str) -> str:
    """
    If card exists for this profile+topic: return its _id
    Else: insert new card with default SM-2 values, return _id
    """
    existing = cards_col.find_one({"profile_id": profile_id, "topic": topic})
    if existing:
        return str(existing["_id"])
        
    new_card = {
        "profile_id": profile_id,
        "topic": topic,
        "subject": subject,
        "source": source,
        "repetitions": 0,
        "easiness": 2.5,
        "interval": 1,
        "next_review_date": date.today().isoformat(),
        "mastery_score": 0,
        "history": [],
        "created_at": datetime.utcnow()
    }
    res = cards_col.insert_one(new_card)
    return str(res.inserted_id)

def get_due_cards(profile_id: str) -> list:
    """Return all cards where next_review_date <= today, sorted by next_review_date"""
    today = date.today().isoformat()
    cursor = cards_col.find({
        "profile_id": profile_id,
        "next_review_date": {"$lte": today}
    }).sort("next_review_date", ASCENDING)
    return [serialize(doc) for doc in cursor]

def get_all_cards(profile_id: str) -> list:
    """Return all cards for profile, sorted by subject then topic"""
    cursor = cards_col.find({"profile_id": profile_id}).sort([
        ("subject", ASCENDING),
        ("topic", ASCENDING)
    ])
    return [serialize(doc) for doc in cursor]

def update_card_after_review(card_id: str, sm2_result: dict, quality: int) -> None:
    """
    Update card with new sm2_result values.
    Append to history, recalculate mastery_score.
    """
    easiness = sm2_result["easiness"]
    interval = sm2_result["interval"]
    
    # Calculate mastery: min(100, (easiness-1.3)/(4.0-1.3)*60 + interval/30*40)
    mastery = (easiness - 1.3) / (4.0 - 1.3) * 60 + (interval / 30.0) * 40
    mastery_score = max(0, min(100, int(mastery)))

    history_entry = {
        "date": date.today().isoformat(),
        "quality": quality,
        "interval": interval
    }

    cards_col.update_one(
        {"_id": ObjectId(card_id)},
        {
            "$set": {
                "repetitions": sm2_result["repetitions"],
                "easiness": easiness,
                "interval": interval,
                "next_review_date": sm2_result["next_review_date"],
                "mastery_score": mastery_score
            },
            "$push": {
                "history": history_entry
            }
        }
    )

def get_knowledge_graph(profile_id: str) -> dict:
    """
    Returns summary grouped by subject.
    {
      "Physics": {
        "total": int,
        "mastered": int,
        "due": int,
        "topics": [{ topic, mastery_score, next_review_date }]
      }
    }
    """
    today = date.today().isoformat()
    all_cards = list(cards_col.find({"profile_id": profile_id}))
    
    graph = {}
    for doc in all_cards:
        subject = doc.get("subject", "Unknown")
        if subject not in graph:
            graph[subject] = {
                "total": 0,
                "mastered": 0,
                "due": 0,
                "topics": []
            }
            
        grp = graph[subject]
        grp["total"] += 1
        
        m_score = doc.get("mastery_score", 0)
        if m_score >= 75:
            grp["mastered"] += 1
            
        next_d = doc.get("next_review_date", "")
        if next_d <= today:
            grp["due"] += 1
            
        grp["topics"].append({
            "_id": str(doc["_id"]),
            "topic": doc.get("topic"),
            "mastery_score": m_score,
            "next_review_date": next_d,
            "interval": doc.get("interval", 1)
        })
        
    return graph
