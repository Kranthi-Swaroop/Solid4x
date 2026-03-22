import uuid
import random
from datetime import datetime
import hdbscan
import numpy as np
from collections import defaultdict
from app.core.database import get_database
from app.core.vector_db import get_vector_db
from app.core.config import settings
from app.schemas.test import MockTestResponse, TestAnalysisResponse
from app.schemas.question import QuestionResponse

class TestGeneratorService:
    @staticmethod
    async def generate_mock_test(user_id: str, subjects: list) -> MockTestResponse:
        from app.services.adaptive_practice import AdaptivePracticeService
        from app.services.spaced_repetition import SpacedRepetitionService
        
        db = await get_database()
        vector_collection = get_vector_db()
        questions = db[settings.MONGODB_DB_NAME]['questions']

        solved_ids = await AdaptivePracticeService.get_solved_correctly_ids(user_id)
        due_reviews = await SpacedRepetitionService.get_due_reviews(user_id)
        due_topics = [review['topic'] for review in due_reviews] if due_reviews else []

        questions_by_subject = {}

        for subject in subjects:
            # We strictly need 20 MCQs and 10 NVQs (integer type)
            # Step 1: Query larger pools to prepare for HDBSCAN clustering
            match_base = {"subject": subject.lower(), "question_id": {"$nin": solved_ids}}
            
            mcq_pool = []
            nvq_pool = []
            
            # Biased Density: Pull heavily from Neo4j decayed topics first
            if due_topics:
                mcq_due_cursor = questions.aggregate([
                    { "$match": { **match_base, "type": "mcq", "topic": {"$in": due_topics} } },
                    { "$sample": { "size": 60 } }
                ])
                mcq_pool.extend(await mcq_due_cursor.to_list(length=60))
                
                nvq_due_cursor = questions.aggregate([
                    { "$match": { **match_base, "type": "integer", "topic": {"$in": due_topics} } },
                    { "$sample": { "size": 30 } }
                ])
                nvq_pool.extend(await nvq_due_cursor.to_list(length=30))

            # Fill the remaining mathematical variance randomly maintaining strict limits
            mcq_random_cursor = questions.aggregate([
                { "$match": { **match_base, "type": "mcq" } },
                { "$sample": { "size": 100 } }
            ])
            mcq_pool.extend(await mcq_random_cursor.to_list(length=100))
            
            nvq_random_cursor = questions.aggregate([
                { "$match": { **match_base, "type": "integer" } },
                { "$sample": { "size": 50 } }
            ])
            nvq_pool.extend(await nvq_random_cursor.to_list(length=50))
            
            def unique_pool(pool):
                seen = set()
                res = []
                for q in pool:
                    if q['question_id'] not in seen:
                        seen.add(q['question_id'])
                        res.append(q)
                return res
                
            mcq_pool = unique_pool(mcq_pool)
            nvq_pool = unique_pool(nvq_pool)

            def get_diverse_subset(pool, required_count):
                if len(pool) <= required_count:
                    return pool

                # Fetch embeddings from Chroma via question_id mapping
                question_ids = [str(q['question_id']) for q in pool]
                chroma_result = vector_collection.get(ids=question_ids, include=["embeddings"])
                
                # Create a mapping of id -> embedding
                emb_map = {id_: emb for id_, emb in zip(chroma_result['ids'], chroma_result['embeddings'])}
                
                valid_pool = [q for q in pool if str(q['question_id']) in emb_map]
                if len(valid_pool) <= required_count:
                    return valid_pool
                
                embeddings_array = np.array([emb_map[str(q['question_id'])] for q in valid_pool])
                
                # HDBSCAN Density-based Clustering to group visually/mathematically identical patterns
                clusterer = hdbscan.HDBSCAN(min_cluster_size=2)
                labels = clusterer.fit_predict(embeddings_array)

                clusters = defaultdict(list)
                for q, label in zip(valid_pool, labels):
                    clusters[label].append(q)

                selected = []
                
                # Sequentially pick 1 question per dense cluster to maintain variance
                while len(selected) < required_count:
                    added_in_round = False
                    for label in list(clusters.keys()):
                        if clusters[label]:
                            idx = random.randint(0, len(clusters[label])-1)
                            # Remove the selected question from the cluster to prevent duplicates
                            selected.append(clusters[label].pop(idx))
                            added_in_round = True
                            if len(selected) == required_count:
                                break
                    if not added_in_round:
                        break # Prevents infinite loop if clusters are exhausted before requirement

                return selected

            final_mcqs = get_diverse_subset(mcq_pool, 20)
            final_nvqs = get_diverse_subset(nvq_pool, 10)

            subject_questions = []
            # Convert to strictly typed QuestionResponse
            for q in final_mcqs + final_nvqs:
                q['question_id'] = str(q['question_id'])
                subject_questions.append(QuestionResponse(**q))
            
            questions_by_subject[subject] = subject_questions

        test_id = str(uuid.uuid4())
        
        mock_test_doc = {
            "test_id": test_id,
            "user_id": user_id,
            "subjects": subjects,
            "questions_by_subject": {sub: [q.model_dump() for q in qlist] for sub, qlist in questions_by_subject.items()},
            "total_questions": 75,
            "section_a_mcq_count": 60,
            "section_b_nvq_count": 15,
            "created_at": datetime.utcnow()
        }
        await db[settings.MONGODB_DB_NAME]['mock_tests'].insert_one(mock_test_doc)

        return MockTestResponse(
            test_id=test_id,
            questions_by_subject=questions_by_subject,
            total_questions=75,
            section_a_mcq_count=60,
            section_b_nvq_count=15
        )

    @staticmethod
    async def analyze_submission(user_id: str, test_id: str, answers: list):
        from app.services.analytics import AnalyticsService
        from app.services.spaced_repetition import SpacedRepetitionService
        
        class PayloadObj:
            pass
        payload = PayloadObj()
        payload.user_id = user_id
        payload.test_id = test_id
        payload.answers = answers
        
        analysis = await AnalyticsService.process_mock_submission(payload)
        
        db = await get_database()
        questions = db[settings.MONGODB_DB_NAME]['questions']
        progress_collection = db[settings.MONGODB_DB_NAME]['user_progress']
        
        q_ids = [ans.question_id for ans in answers]
        cursor = questions.find({"question_id": {"$in": q_ids}})
        raw_docs = await cursor.to_list(length=len(q_ids))
        doc_map = {str(d['question_id']): d for d in raw_docs}
        
        from datetime import datetime
        now = datetime.utcnow()
        progress_docs = []
        
        for ans in answers:
            if ans.question_id not in doc_map: continue
            doc = doc_map[ans.question_id]
            
            progress_docs.append({
                "user_id": user_id,
                "question_id": ans.question_id,
                "is_correct": ans.is_correct,
                "time_spent": ans.time_spent,
                "timestamp": now
            })
            
            await SpacedRepetitionService.update_knowledge_graph(
                user_id=user_id,
                subject=doc.get("subject", "unknown"),
                chapter=doc.get("chapter", "unknown"),
                topic=doc.get("topic", "unknown"),
                is_correct=ans.is_correct
            )
            
        if progress_docs:
            await progress_collection.insert_many(progress_docs)
            
        return TestAnalysisResponse(
            score=analysis["final_score"],
            weak_areas=analysis["weak_areas"],
            strong_areas=analysis["strong_areas"],
            time_spent_analysis={}
        )

    @staticmethod
    async def get_user_mock_tests(user_id: str):
        db = await get_database()
        cursor = db[settings.MONGODB_DB_NAME]['mock_tests'].find({"user_id": user_id}, {"_id": 0})
        tests = await cursor.to_list(length=100)
        return tests
