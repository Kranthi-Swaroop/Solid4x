from neo4j import AsyncGraphDatabase
from app.core.config import settings

class Neo4jDB:
    driver = None

neo4j_db = Neo4jDB()

async def connect_to_neo4j():
    neo4j_db.driver = AsyncGraphDatabase.driver(
        settings.NEO4J_URI, 
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )

async def close_neo4j_connection():
    if neo4j_db.driver:
        await neo4j_db.driver.close()

def get_neo4j_driver():
    return neo4j_db.driver
