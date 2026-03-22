from app.core.vector_db import get_vector_db
from app.core.database import get_database
from app.core.config import settings
from app.schemas.question import QuestionResponse
from datetime import datetime

class AdaptivePracticeService:
    @staticmethod
    async def get_similar_questions(question_id: str, limit: int = 5):
        vector_collection = get_vector_db()
        db = await get_database()
        questions = db[settings.MONGODB_DB_NAME]['questions']

        try:
            # 0. Fetch the target metadata to restrict results to same Chapter
            target_question = await questions.find_one({"question_id": question_id})
            if not target_question:
                return []
            
            target_subject = target_question.get('subject')
            target_chapter = target_question.get('chapter')

            # 1. Fetch exact embedding footprint of the failed question
            target_res = vector_collection.get(ids=[question_id], include=["embeddings"])
            
            if not target_res or len(target_res.get('embeddings', [])) == 0:
                return []
                
            target_embedding = target_res['embeddings'][0]
            
            # 2. Run K-Nearest Neighbors via ChromaDB
            # Over-fetch heavily across the global DB so we can trim down mathematically to the specific chapter
            results = vector_collection.query(
                query_embeddings=[target_embedding],
                n_results=100
            )
            
            if not results or not results['ids']:
                return []
            
            similar_ids = results['ids'][0]
            
            # 3. Exclude the absolute match
            filtered_ids = [sid for sid in similar_ids if sid != question_id]
            
            # 4. Hydrate the metadata from MongoDB explicitly strictly matching Domain Parity
            cursor = questions.find({
                "question_id": {"$in": filtered_ids},
                "subject": target_subject,
                "chapter": target_chapter
            })
            raw_docs = await cursor.to_list(length=100)
            
            # 5. MongoDB find() loses order. Re-map directly to ChromaDB's absolute nearest-distance ranking!
            doc_map = {str(d['question_id']): d for d in raw_docs}
            
            final_pool = []
            for sid in filtered_ids:
                if sid in doc_map:
                    doc = doc_map[sid]
                    doc['question_id'] = str(doc['question_id'])
                    final_pool.append(doc)
                    if len(final_pool) == limit:
                        break
            
            return final_pool
            
        except Exception as e:
            print(f"Vector search failed: {e}")
            return []

    @staticmethod
    async def analyze_error_rates(user_id: str, question_id: str, is_correct: bool, time_spent: int):
        db = await get_database()
        progress_collection = db[settings.MONGODB_DB_NAME]['user_progress']
        
        await progress_collection.insert_one({
            "user_id": user_id,
            "question_id": question_id,
            "is_correct": is_correct,
            "time_spent": time_spent,
            "timestamp": datetime.utcnow()
        })
        
        questions = db[settings.MONGODB_DB_NAME]['questions']
        doc = await questions.find_one({"question_id": question_id})
        if doc:
            from app.services.spaced_repetition import SpacedRepetitionService
            await SpacedRepetitionService.update_knowledge_graph(
                user_id=user_id,
                subject=doc.get("subject", "unknown"),
                chapter=doc.get("chapter", "unknown"),
                topic=doc.get("topic", "unknown"),
                is_correct=is_correct
            )
        
        return True

    @staticmethod
    async def get_solved_correctly_ids(user_id: str) -> list[str]:
        db = await get_database()
        progress = db[settings.MONGODB_DB_NAME]['user_progress']
        cursor = progress.find({"user_id": user_id, "is_correct": True}, {"question_id": 1})
        docs = await cursor.to_list(length=50000)
        return list(set(d["question_id"] for d in docs))

    @staticmethod
    async def generate_practice_questions(user_id: str, chapter: str = None, topic: str = None, limit: int = 5):
        db = await get_database()
        questions = db[settings.MONGODB_DB_NAME]['questions']
        
        solved_ids = await AdaptivePracticeService.get_solved_correctly_ids(user_id)
        
        match_query = {"question_id": {"$nin": solved_ids}}
        if chapter:
            match_query["chapter"] = chapter
        if topic:
            match_query["topic"] = topic
            
        cursor = questions.aggregate([
            {"$match": match_query},
            {"$sample": {"size": limit}}
        ])
        
        docs = await cursor.to_list(length=limit)
        return [QuestionResponse(**doc) for doc in docs]
