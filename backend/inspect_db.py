import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import json

async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.campuscode
    
    # Get one numerical question
    q = await db.questions.find_one({"type": "integer"})
    if not q:
        q = await db.questions.find_one({"type": "numerical"})
    
    print("Numerical Schema:")
    print(json.dumps(q, default=str, indent=2) if q else "No numerical questions found")

asyncio.run(main())
