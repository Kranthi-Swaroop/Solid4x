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
            # 1. Fetch exact embedding footprint of the failed question
            target_res = vector_collection.get(ids=[question_id], include=["embeddings"])
            
            if not target_res or not target_res['embeddings']:
                return []
                
            target_embedding = target_res['embeddings'][0]
            
            # 2. Run K-Nearest Neighbors via ChromaDB
            # limit+1 because the exact question itself will logically be the first match
            results = vector_collection.query(
                query_embeddings=[target_embedding],
                n_results=limit + 1
            )
            
            if not results or not results['ids']:
                return []
            
            similar_ids = results['ids'][0]
            
            # 3. Exclude the absolute match and constrain to limit
            filtered_ids = [sid for sid in similar_ids if sid != question_id][:limit]
            
            # 4. Hydrate the metadata from MongoDB
            cursor = questions.find({"question_id": {"$in": filtered_ids}})
            raw_docs = await cursor.to_list(length=limit)
            
            # Convert accurately to QuestionResponse models
            final_pool = []
            for doc in raw_docs:
                doc['question_id'] = str(doc['question_id'])
                final_pool.append(doc)
            
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
        
        # If the student got it wrong or struggled on it (120+ seconds), surface targeted K-NN vectors immediately
        if not is_correct or time_spent > 120:
            return await AdaptivePracticeService.get_similar_questions(question_id, limit=3)
        return []
