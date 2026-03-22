import google.generativeai as genai
import os
import json
from datetime import date, datetime
from app.core.database import get_database
from app.core.config import settings

JEE_SYLLABUS = {
    "Physics": [
        "Mechanics", "Thermodynamics", "Electrostatics", "Optics", 
        "Modern Physics", "Waves", "Magnetism"
    ],
    "Chemistry": [
        "Mole Concept", "Electrochemistry", "Organic Reactions", 
        "Equilibrium", "Coordination Chemistry", "Thermochemistry", 
        "Chemical Bonding"
    ],
    "Mathematics": [
        "Calculus", "Algebra", "Coordinate Geometry", 
        "Trigonometry", "Vectors", "Probability", "Matrices"
    ]
}

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(model_name="gemma-3-27b-it")

class PlannerService:
    @staticmethod
    def days_remaining(exam_date: str) -> int:
        delta = datetime.strptime(exam_date, "%Y-%m-%d").date() - date.today()
        return max(delta.days, 1)

    @staticmethod
    def clean_json(text: str) -> dict:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text.replace("json", "", 1)
        return json.loads(text.strip())

    @staticmethod
    def build_prompt(profile: dict, missed: list) -> str:
        return f"""
System Instructions:
You are an autonomous JEE study planner AI. You only respond with raw valid JSON.
No markdown, no explanation, no code fences. Only the JSON object.

Student profile:
- Name: {profile.get('name', 'Student')}
- Exam date: {profile['exam_date']} ({PlannerService.days_remaining(profile['exam_date'])} days left)
- Daily study hours: {profile['daily_hours']}
- Weak areas: {', '.join(profile.get('weak_areas', []))}

JEE Syllabus:
{json.dumps(JEE_SYLLABUS, indent=2)}

Missed sessions to reschedule:
{json.dumps(missed, indent=2) if missed else "None"}

Rules:
1. Generate a 7-day plan starting from tomorrow
2. Total session duration per day must not exceed {profile['daily_hours']} hours (= {int(profile['daily_hours'])*60} mins)
3. Cover all 3 subjects — never skip a subject for more than 2 days
4. Prioritize weak areas but do not ignore strong ones
5. If missed sessions exist, redistribute those topics into upcoming days
6. Give a specific one-line reason per session referencing JEE weightage or student weakness
7. Return ONLY the raw JSON object in exactly this format:

{{
  "plan": [
    {{
      "date": "YYYY-MM-DD",
      "sessions": [
        {{
          "topic": "topic name",
          "subject": "Physics|Chemistry|Mathematics",
          "duration_mins": 60,
          "priority": "high|medium|low",
          "reason": "one line reason"
        }}
      ]
    }}
  ]
}}
"""

    @staticmethod
    async def save_profile(profile: dict, user_id: str):
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
    async def generate_plan(profile: dict, user_id: str, missed: list = []) -> dict:
        prompt = PlannerService.build_prompt(profile, missed)
        response = model.generate_content(prompt)
        plan = PlannerService.clean_json(response.text)

        sessions_to_save = []
        for day in plan.get("plan", []):
            for session in day.get("sessions", []):
                sessions_to_save.append({
                    **session,
                    "date": day["date"],
                    "status": "pending",
                    "user_id": user_id,
                })
        await PlannerService.save_profile(profile, user_id)
        await PlannerService.save_sessions(sessions_to_save)
        return plan

    @staticmethod
    async def rebalance_plan(profile: dict, user_id: str) -> dict:
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
