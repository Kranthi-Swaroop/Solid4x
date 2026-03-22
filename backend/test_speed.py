import asyncio
import os
import sys
import time

sys.path.append(os.getcwd())
from app.services.test_generator import TestGeneratorService
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.vector_db import connect_to_chroma

async def run():
    print("Connecting DB")
    t0 = time.time()
    await connect_to_mongo()
    connect_to_chroma()
    t1 = time.time()
    print(f"Connected DB in {t1-t0:.2f}s")
    
    print("Starting generation")
    res = await TestGeneratorService.generate_mock_test('user1', ['Physics'])
    t2 = time.time()
    print(f"Generated {len(res.questions)} in {t2-t1:.2f}s")
    
    await close_mongo_connection()

asyncio.run(run())
