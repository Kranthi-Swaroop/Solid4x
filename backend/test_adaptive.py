import asyncio
import os
import sys

sys.path.append(os.getcwd())
from app.services.adaptive_practice import AdaptivePracticeService
from app.core.database import connect_to_mongo, db, close_mongo_connection
from app.core.vector_db import connect_to_chroma, get_vector_db

async def run():
    await connect_to_mongo()
    connect_to_chroma()
    
    qid = "2yrP77y91dEoBdH3"
    print(f"Testing ID: {qid}")
    
    vector_collection = get_vector_db()
    res = vector_collection.get(ids=[qid], include=["embeddings"])
    print("Chroma target return:", bool(res.get('embeddings')))
    
    if res.get('embeddings'):
        print("Querying Chroma K-NN...")
        knn = vector_collection.query(query_embeddings=[res['embeddings'][0]], n_results=5)
        print("K-NN Ids:", knn['ids'])
    
    print("Testing full pipeline...")
    try:
        res2 = await AdaptivePracticeService.get_similar_questions(qid, 5)
        print(f"Service returned {len(res2)} questions")
    except Exception as e:
        print(f"Err: {e}")
    
    await close_mongo_connection()

asyncio.run(run())
