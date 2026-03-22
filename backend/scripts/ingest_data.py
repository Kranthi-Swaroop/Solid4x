import sys
import os
import json
import numpy as np
import asyncio

# Setup path so we can import app modules directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db, connect_to_mongo, close_mongo_connection
from app.core.vector_db import vector_db, connect_to_chroma
from app.core.config import settings

async def ingest_json(file_path: str):
    print(f"Loading structured data from {file_path}")
    with open(file_path, "r") as f:
        data = json.load(f)
    print(f"Loaded {len(data)} items. Ingesting to MongoDB...")
    
    collection = db.client[settings.MONGODB_DB_NAME]["questions"]
    
    # Process in batches to prevent overwhelming memory/payload sizes
    batch_size = 1000
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        await collection.insert_many(batch)
        print(f"Inserted MongoDB batch {min(i + batch_size, len(data))}/{len(data)}")

    print("MongoDB ingestion complete.")

def ingest_npz(file_path: str):
    print(f"Loading embeddings from {file_path}")
    data = np.load(file_path)
    question_ids = data['question_ids'].tolist()
    embeddings = data['embeddings'].tolist()
    print(f"Loaded {len(question_ids)} embeddings. Ingesting to ChromaDB...")
    
    collection = vector_db.collection
    
    # Process in batches for ChromaDB as well
    batch_size = 1000
    for i in range(0, len(question_ids), batch_size):
        batch_ids = question_ids[i:i + batch_size]
        batch_embeddings = embeddings[i:i + batch_size]
        collection.add(
            ids=batch_ids,
            embeddings=batch_embeddings
        )
        print(f"Inserted ChromaDB batch {min(i + batch_size, len(question_ids))}/{len(question_ids)}")

    print("ChromaDB ingestion complete.")

async def main():
    print("Connecting to databases...")
    await connect_to_mongo()
    connect_to_chroma()

    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "pyqs_structured_data.json")
    npz_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "pyqs_embeddings.npz")

    if os.path.exists(json_path):
        await ingest_json(json_path)
    else:
        print(f"File not found: {json_path}")
        
    if os.path.exists(npz_path):
        ingest_npz(npz_path)
    else:
        print(f"File not found: {npz_path}")
    
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())
