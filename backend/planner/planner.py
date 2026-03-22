import google.generativeai as genai
import os
import json
from .syllabus import JEE_SYLLABUS
from .database import save_sessions, get_missed_sessions
from datetime import date, datetime

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel(
    model_name="gemini-2.5-pro-preview-03-25",
    system_instruction=(
        "You are an autonomous JEE study planner AI. "
        "You only respond with raw valid JSON. "
        "No markdown, no explanation, no code fences. "
        "Only the JSON object."
    ),
)


def days_remaining(exam_date: str) -> int:
    delta = datetime.strptime(exam_date, "%Y-%m-%d").date() - date.today()
    return max(delta.days, 1)


def clean_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def build_prompt(profile: dict, missed: list) -> str:
    return f"""
Student profile:
- Name: {profile['name']}
- Exam date: {profile['exam_date']} ({days_remaining(profile['exam_date'])} days left)
- Daily study hours: {profile['daily_hours']}
- Weak areas: {', '.join(profile['weak_areas'])}

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


def generate_plan(profile: dict, profile_id: str, missed: list = []) -> dict:
    prompt = build_prompt(profile, missed)
    response = model.generate_content(prompt)
    plan = clean_json(response.text)

    # Attach profile_id and status to each session before saving
    sessions_to_save = []
    for day in plan["plan"]:
        for session in day["sessions"]:
            sessions_to_save.append({
                **session,
                "date": day["date"],
                "status": "pending",
                "profile_id": profile_id,
            })

    save_sessions(sessions_to_save)
    return plan


def rebalance_plan(profile: dict, profile_id: str) -> dict:
    missed = get_missed_sessions(profile_id)
    missed_clean = [{"topic": m["topic"], "date": m["date"]} for m in missed]
    return generate_plan(profile, profile_id, missed=missed_clean)
