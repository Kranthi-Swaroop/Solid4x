import uuid
import random
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
        db = await get_database()
        vector_collection = get_vector_db()
        questions = db[settings.MONGODB_DB_NAME]['questions']

        questions_by_subject = {}

        for subject in subjects:
            # We strictly need 20 MCQs and 10 NVQs (integer type)
            # Step 1: Query larger pools to prepare for HDBSCAN clustering
            mcq_pool_cursor = questions.aggregate([
                { "$match": { "subject": subject.lower(), "type": "mcq" } },
                { "$sample": { "size": 100 } }
            ])
            nvq_pool_cursor = questions.aggregate([
                { "$match": { "subject": subject.lower(), "type": "integer" } },
                { "$sample": { "size": 50 } }
            ])

            mcq_pool = await mcq_pool_cursor.to_list(length=100)
            nvq_pool = await nvq_pool_cursor.to_list(length=50)

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
        return MockTestResponse(
            test_id=test_id,
            questions_by_subject=questions_by_subject,
            total_questions=75,
            section_a_mcq_count=60,
            section_b_nvq_count=15
        )

    @staticmethod
    async def analyze_submission(user_id: str, test_id: str, answers: dict, time_spent: dict):
        # Stub for Mock Analysis logic later
        return TestAnalysisResponse(
            score=0,
            weak_areas={"Physics": "Mechanics"},
            strong_areas={"Mathematics": "Algebra"},
            time_spent_analysis=time_spent
        )
