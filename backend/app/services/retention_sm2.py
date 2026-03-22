from datetime import date, datetime, timedelta
from app.core.database import get_database
from app.core.config import settings
from bson import ObjectId

MIN_EASINESS = 1.3

class RetentionService:
    @staticmethod
    def sm2(quality: int, repetitions: int, easiness: float, interval: int) -> dict:
        if quality < 3:
            repetitions = 0
            interval = 1
        else:
            if repetitions == 0:
                interval = 1
            elif repetitions == 1:
                interval = 6
            else:
                interval = round(interval * easiness)
            repetitions += 1
        easiness = max(MIN_EASINESS, easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        next_review = date.today() + timedelta(days=interval)
        return {
            "repetitions": repetitions,
            "easiness": round(easiness, 4),
            "interval": interval,
            "next_review_date": next_review.isoformat()
        }

    @staticmethod
    async def upsert_card(user_id: str, topic: str, subject: str, source: str) -> str:
        db = await get_database()
        cards_col = db[settings.MONGODB_DB_NAME]["concept_cards"]
        existing = await cards_col.find_one({"user_id": user_id, "topic": topic})
        if existing:
            return str(existing["_id"])
            
        new_card = {
            "user_id": user_id,
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
        res = await cards_col.insert_one(new_card)
        return str(res.inserted_id)

    @staticmethod
    async def get_due_cards(user_id: str) -> list:
        db = await get_database()
        today = date.today().isoformat()
        cursor = db[settings.MONGODB_DB_NAME]["concept_cards"].find({
            "user_id": user_id,
            "next_review_date": {"$lte": today}
        }).sort("next_review_date", 1)
        cards = await cursor.to_list(length=None)
        for c in cards: c["_id"] = str(c["_id"])
        return cards

    @staticmethod
    async def get_all_cards(user_id: str) -> list:
        db = await get_database()
        cursor = db[settings.MONGODB_DB_NAME]["concept_cards"].find({"user_id": user_id}).sort([
            ("subject", 1), ("topic", 1)
        ])
        cards = await cursor.to_list(length=None)
        for c in cards: c["_id"] = str(c["_id"])
        return cards

    @staticmethod
    async def process_review(card_id: str, quality: int):
        db = await get_database()
        cards_col = db[settings.MONGODB_DB_NAME]["concept_cards"]
        doc = await cards_col.find_one({"_id": ObjectId(card_id)})
        if not doc:
            raise Exception("Card not found")
        sm2_result = RetentionService.sm2(quality, doc.get("repetitions",0), doc.get("easiness",2.5), doc.get("interval",1))
        
        easiness = sm2_result["easiness"]
        interval = sm2_result["interval"]
        mastery = (easiness - 1.3) / (4.0 - 1.3) * 60 + (interval / 30.0) * 40
        mastery_score = max(0, min(100, int(mastery)))

        history_entry = {
            "date": date.today().isoformat(),
            "quality": quality,
            "interval": interval
        }

        # Synchronize with Neo4j Global Knowledge Graph mathematically
        from app.services.spaced_repetition import SpacedRepetitionService
        is_correct = (quality >= 3)
        await SpacedRepetitionService.update_topic_strength(
            user_id=doc.get("user_id"),
            topic=doc.get("topic", "Unknown"),
            is_correct=is_correct
        )

        await cards_col.update_one(
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
        doc = await cards_col.find_one({"_id": ObjectId(card_id)})
        doc["_id"] = str(doc["_id"])
        return {
            "updated_card": doc,
            "next_review_date": sm2_result["next_review_date"],
            "interval": sm2_result["interval"],
            "mastery_score": mastery_score
        }

    @staticmethod
    async def get_knowledge_graph(user_id: str) -> dict:
        db = await get_database()
        today = date.today().isoformat()
        cursor = db[settings.MONGODB_DB_NAME]["concept_cards"].find({"user_id": user_id})
        all_cards = await cursor.to_list(length=None)
        graph = {}
        for doc in all_cards:
            subject = doc.get("subject", "Unknown")
            if subject not in graph:
                graph[subject] = {"total": 0, "mastered": 0, "due": 0, "topics": []}
            grp = graph[subject]
            grp["total"] += 1
            m_score = doc.get("mastery_score", 0)
            if m_score >= 75: grp["mastered"] += 1
            next_d = doc.get("next_review_date", "")
            if next_d <= today: grp["due"] += 1
            grp["topics"].append({
                "_id": str(doc["_id"]),
                "topic": doc.get("topic"),
                "mastery_score": m_score,
                "next_review_date": next_d,
                "interval": doc.get("interval", 1)
            })
        return graph
