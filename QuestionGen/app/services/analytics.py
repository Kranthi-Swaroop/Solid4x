from collections import defaultdict
from app.core.database import get_database
from app.core.config import settings

class AnalyticsService:
    @staticmethod
    async def process_mock_submission(payload):
        db = await get_database()
        questions = db[settings.MONGODB_DB_NAME]['questions']
        
        # Fetch question context to know their subjects and chapters dynamically
        q_ids = [item.question_id for item in payload.answers]
        cursor = questions.find({"question_id": {"$in": q_ids}})
        raw_docs = await cursor.to_list(length=len(q_ids))
        
        doc_map = {str(d['question_id']): d for d in raw_docs}
        
        score = 0
        chapter_stats = defaultdict(lambda: {"correct": 0, "total": 0})
        
        for item in payload.answers:
            if item.question_id not in doc_map:
                continue
            
            doc = doc_map[item.question_id]
            subject = doc.get("subject", "unknown")
            chapter = doc.get("chapter", "unknown")
            
            key = f"{subject}::{chapter}"
            chapter_stats[key]["total"] += 1
            
            if item.is_correct:
                if doc.get("type", "mcq").lower() == "mcq":
                    score += 4
                else:
                    score += 4
                chapter_stats[key]["correct"] += 1
            else:
                if doc.get("type", "mcq").lower() == "mcq":
                    score -= 1
                else:
                    score -= 1 # Modern JEE marking treats NVQ negatives as -1

        # Calculate weak areas explicitly (less than 50% grouping accuracy)
        weak_areas = defaultdict(list)
        strong_areas = defaultdict(list)
        
        for key, stats in chapter_stats.items():
            subject, chapter = key.split("::")
            if stats["total"] > 0:
                acc = stats["correct"] / stats["total"]
                if acc < 0.5:
                    weak_areas[subject].append(chapter)
                else:
                    strong_areas[subject].append(chapter)
        
        return {
            "test_id": payload.test_id,
            "final_score": score,
            "weak_areas": dict(weak_areas),
            "strong_areas": dict(strong_areas)
        }
