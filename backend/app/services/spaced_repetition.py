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
        ON CREATE SET 
            r.strength = CASE WHEN $is_correct THEN 1.0 ELSE 0.0 END,
            r.correct_count = CASE WHEN $is_correct THEN 1 ELSE 0 END,
            r.incorrect_count = CASE WHEN $is_correct THEN 0 ELSE 1 END,
            r.last_reviewed = datetime()
        ON MATCH SET 
            r.correct_count = coalesce(r.correct_count, 0) + CASE WHEN $is_correct THEN 1 ELSE 0 END,
            r.incorrect_count = coalesce(r.incorrect_count, 0) + CASE WHEN $is_correct THEN 0 ELSE 1 END,
            r.strength = CASE 
                WHEN (r.strength + $change) < 0 THEN 0.0 
                ELSE r.strength + $change 
            END,
            r.last_reviewed = datetime()
        """
        change = 1.0 if is_correct else -0.3
        async with driver.session() as session:
            await session.run(query, user_id=user_id, subject=subject, chapter=chapter, topic=topic, change=change, is_correct=is_correct)

    @staticmethod
    async def update_topic_strength(user_id: str, topic: str, is_correct: bool):
        driver = get_neo4j_driver()
        query = """
        MERGE (u:User {id: $user_id})
        MERGE (t:Topic {name: $topic})
        MERGE (u)-[r:STUDIED]->(t)
        ON CREATE SET r.strength = CASE WHEN $change > 0 THEN $change ELSE 0.1 END, r.last_reviewed = datetime()
        ON MATCH SET r.strength = r.strength + $change, r.last_reviewed = datetime()
        """
        change = 1.0 if is_correct else -0.5
        async with driver.session() as session:
            await session.run(query, user_id=user_id, topic=topic, change=change)

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

    @staticmethod
    async def get_unpracticed_topics(user_id: str, subject: str) -> list[str]:
        driver = get_neo4j_driver()
        
        query = """
        MATCH (s:Subject {name: toLower($subject)})-[:HAS_CHAPTER]->(c:Chapter)-[:HAS_TOPIC]->(t:Topic)
        WHERE NOT EXISTS {
            MATCH (u:User {id: $user_id})-[r:STUDIED]->(t)
        }
        RETURN t.name AS topic_name
        """
        params = {"user_id": user_id, "subject": subject}
            
        async with driver.session() as session:
            result = await session.run(query, **params)
            records = await result.data()
            return [record['topic_name'] for record in records]

    @staticmethod
    async def get_topics_status(user_id: str):
        driver = get_neo4j_driver()
        query = """
        MATCH (s:Subject)-[:HAS_CHAPTER]->(c:Chapter)-[:HAS_TOPIC]->(t:Topic)
        OPTIONAL MATCH (u:User {id: $user_id})-[r:STUDIED]->(t)
        WITH s.name AS subject, c.name AS chapter, t.name AS topic, r,
             CASE WHEN r IS NOT NULL THEN duration.between(r.last_reviewed, datetime()).days ELSE 0 END AS days_passed
        WITH subject, chapter, topic, r.strength AS strength, 
             CASE WHEN r IS NOT NULL THEN exp(-1.0 * days_passed / CASE WHEN r.strength > 0.1 THEN r.strength ELSE 0.1 END) ELSE null END AS retention
        RETURN subject, chapter, topic, strength, retention
        """
        async with driver.session() as session:
            result = await session.run(query, user_id=user_id)
            records = await result.data()
            
            grouped = {"due": [], "mastered": [], "weak": [], "unpracticed": []}
            for rec in records:
                strength = rec.get("strength")
                retention = rec.get("retention")
                
                if strength is None:
                    status = "unpracticed"
                elif strength >= 3.0 and retention is not None and retention >= 0.7:
                    status = "mastered"
                elif strength < 1.5:
                    status = "weak"
                elif retention is not None and retention < 0.7:
                    status = "due"
                else:
                    status = "weak"
                
                grouped[status].append({
                    "subject": rec.get("subject"),
                    "chapter": rec.get("chapter"),
                    "topic": rec.get("topic"),
                    "strength": round(strength, 2) if strength is not None else None,
                    "retention": round(retention, 3) if retention is not None else None
                })
            return grouped
