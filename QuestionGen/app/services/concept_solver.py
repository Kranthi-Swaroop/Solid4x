from app.core.database import get_database
from app.core.config import settings

class ConceptSolverService:
    @staticmethod
    async def solve_question(question_id: str):
        db = await get_database()
        questions = db[settings.MONGODB_DB_NAME]['questions']
        doc = await questions.find_one({"question_id": question_id})
        
        if not doc:
            return {"error": "Question not found"}
        
        explanation = doc.get("explanation", "No formal explanation exists for this question in the dataset.")
        
        return {
            "question_id": question_id, 
            "explanation": explanation
        }
