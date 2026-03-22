import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from neo4j import AsyncGraphDatabase
from app.core.config import settings

async def main():
    mongo_url = settings.MONGODB_URI
    db_name = settings.MONGODB_DB_NAME
    
    neo4j_uri = settings.NEO4J_URI
    neo4j_user = settings.NEO4J_USER
    neo4j_password = settings.NEO4J_PASSWORD

    print(f"Connecting to MongoDB...")
    mongo_client = AsyncIOMotorClient(mongo_url)
    db = mongo_client[db_name]
    questions = db['questions']
    
    pipeline = [
        {"$group": {"_id": {"subject": "$subject", "chapter": "$chapter", "topic": "$topic"}}}
    ]
    
    unique_combinations = []
    async for doc in questions.aggregate(pipeline):
        mapping = doc["_id"]
        if mapping.get("subject") and mapping.get("chapter") and mapping.get("topic"):
            unique_combinations.append(mapping)
            
    print(f"Found {len(unique_combinations)} unique Subject->Chapter->Topic paths.")

    print(f"Connecting to Neo4j...")
    driver = AsyncGraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    async with driver.session() as session:
        await session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Subject) REQUIRE s.name IS UNIQUE")
        await session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Chapter) REQUIRE c.name IS UNIQUE")
        await session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE")
        
        cypher_query = """
        UNWIND $batch AS row
        MERGE (s:Subject {name: toLower(row.subject)})
        MERGE (c:Chapter {name: toLower(row.chapter)})
        MERGE (t:Topic {name: toLower(row.topic)})
        MERGE (s)-[:HAS_CHAPTER]->(c)
        MERGE (c)-[:HAS_TOPIC]->(t)
        """
        await session.run(cypher_query, batch=unique_combinations)
        
    await driver.close()
    mongo_client.close()
    print("Static curriculum graph mapping perfectly completed!")

if __name__ == "__main__":
    asyncio.run(main())
