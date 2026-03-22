import os
import json
from datetime import date, datetime, timedelta
from app.core.database import get_database
from app.core.config import settings

class PlannerService:
    @staticmethod
    def days_remaining(exam_date: str) -> int:
        delta = datetime.strptime(exam_date, "%Y-%m-%d").date() - date.today()
        return max(delta.days, 1)

    @staticmethod
    async def generate_plan(profile: dict, user_id: str, missed: list = []) -> dict:
        from app.services.spaced_repetition import SpacedRepetitionService
        
        due_reviews = await SpacedRepetitionService.get_due_reviews(user_id)
        
        sessions_to_save = []
        today = date.today()
        sessions_per_day = int(profile.get('daily_hours', 3))
        
        queue = []
        for m in missed:
            queue.append({"topic": m["topic"], "subject": m.get("subject", "Unknown"), "priority": "high", "reason": "Missed session"})
            
        for r in due_reviews:
            queue.append({"topic": r["topic"], "subject": r.get("subject", "Unknown"), "priority": "high", "reason": "Decayed memory strictly requires review"})
            
        for subject in ["physics", "chemistry", "mathematics"]:
            unpracticed = await SpacedRepetitionService.get_unpracticed_topics(user_id, subject)
            display_sub = subject.capitalize()
            for topic in unpracticed:
                queue.append({"topic": topic, "subject": display_sub, "priority": "medium", "reason": "Unpracticed curriculum sequence"})

        seen = set()
        clean_queue = []
        for q in queue:
            if q["topic"] not in seen:
                seen.add(q["topic"])
                clean_queue.append(q)

        plan = []
        q_idx = 0
        for day_offset in range(1, 8):
            day_date = (today + timedelta(days=day_offset)).isoformat()
            day_sessions = []
            
            for _ in range(sessions_per_day):
                if q_idx < len(clean_queue):
                    task = clean_queue[q_idx]
                    q_idx += 1
                    day_sessions.append({
                        "topic": task["topic"],
                        "subject": task["subject"],
                        "duration_mins": 60,
                        "priority": task["priority"],
                        "reason": task["reason"]
                    })
                    sessions_to_save.append({
                         "topic": task["topic"],
                         "subject": task["subject"],
                         "duration_mins": 60,
                         "priority": task["priority"],
                         "reason": task["reason"],
                         "date": day_date,
                         "status": "pending",
                         "user_id": user_id
                    })
            plan.append({
                "date": day_date,
                "sessions": day_sessions
            })

        await PlannerService.save_profile(profile, user_id)
        await PlannerService.save_sessions(sessions_to_save)
        return {"plan": plan}
        db = await get_database()
        profile["user_id"] = user_id
        await db[settings.MONGODB_DB_NAME]["profiles"].update_one(
            {"user_id": user_id},
            {"$set": profile},
            upsert=True
        )

    @staticmethod
    async def get_missed_sessions(user_id: str) -> list:
        db = await get_database()
        cursor = db[settings.MONGODB_DB_NAME]["sessions"].find(
            {"user_id": user_id, "status": "missed"}
        ).sort("date", 1)
        return await cursor.to_list(length=None)

    @staticmethod
    async def save_sessions(sessions: list):
        if sessions:
            db = await get_database()
            await db[settings.MONGODB_DB_NAME]["sessions"].insert_many(sessions)

    @staticmethod
    async def save_profile(profile: dict, user_id: str):
        missed = await PlannerService.get_missed_sessions(user_id)
        missed_clean = [{"topic": m["topic"], "date": m["date"]} for m in missed]
        return await PlannerService.generate_plan(profile, user_id, missed=missed_clean)

    @staticmethod
    async def get_sessions(user_id: str) -> list:
        db = await get_database()
        cursor = db[settings.MONGODB_DB_NAME]["sessions"].find(
            {"user_id": user_id}
        ).sort("date", 1)
        sessions = await cursor.to_list(length=None)
        for s in sessions:
            s["_id"] = str(s["_id"])
        return sessions

    @staticmethod
    async def update_session_status(session_id: str, status: str, user_id: str):
        db = await get_database()
        from bson import ObjectId
        await db[settings.MONGODB_DB_NAME]["sessions"].update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"status": status}}
        )
        if status == "done":
            session = await db[settings.MONGODB_DB_NAME]["sessions"].find_one({"_id": ObjectId(session_id)})
            if session:
                from app.services.retention_sm2 import RetentionService
                await RetentionService.upsert_card(
                    user_id=user_id,
                    topic=session.get("topic", "Unknown"),
                    subject=session.get("subject", "Unknown"),
                    source="planner_done"
                )
