from app.core.neo4j_db import get_neo4j_driver

class SpacedRepetitionService:
    @staticmethod
    async def update_knowledge_graph(user_id: str, subject: str, chapter: str, topic: str, is_correct: bool):
        driver = get_neo4j_driver()
        query = """
        MERGE (u:User {id: $user_id})
        MERGE (s:Subject {name: $subject})
        MERGE (c:Chapter {name: $chapter})
        MERGE (t:Topic {name: $topic})
        MERGE (s)-[:HAS_CHAPTER]->(c)
        MERGE (c)-[:HAS_TOPIC]->(t)
        
        MERGE (u)-[r:STUDIED]->(t)
        ON CREATE SET r.strength = $change, r.last_reviewed = datetime()
        ON MATCH SET r.strength = r.strength + $change, r.last_reviewed = datetime()
        """
        change = 1.0 if is_correct else -0.5
        async with driver.session() as session:
            await session.run(query, user_id=user_id, subject=subject, chapter=chapter, topic=topic, change=change)

    @staticmethod
    async def get_due_reviews(user_id: str):
        driver = get_neo4j_driver()
        # Forgetting curve: R = e^(-t/S) where S is strength. If R < 0.7, review is due.
        # Computed directly inside Neo4j engine to avoid mapping thousands of nodes into Python RAM
        query = """
        MATCH (u:User {id: $user_id})-[r:STUDIED]->(t:Topic)
        WITH t, r, duration.between(r.last_reviewed, datetime()).days AS days_passed
        WITH t, exp(-1.0 * days_passed / CASE WHEN r.strength > 0.1 THEN r.strength ELSE 0.1 END) AS retention
        WHERE retention < 0.7
        RETURN t.name AS topic, retention
        ORDER BY retention ASC
        LIMIT 10
        """
        async with driver.session() as session:
            result = await session.run(query, user_id=user_id)
            records = await result.data()
            return records
