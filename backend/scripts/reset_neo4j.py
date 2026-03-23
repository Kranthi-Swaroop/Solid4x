#!/usr/bin/env python3
"""
Direct Neo4j manipulation script.
Resets negative strengths and sets up realistic test data
to demonstrate all 4 retention dashboard categories.
"""
import asyncio
from neo4j import AsyncGraphDatabase

URI = "bolt://168.119.148.180:7687"
USER = "neo4j"
PASSWORD = "6391z8fk2JTAcrchN2un"

async def main():
    driver = AsyncGraphDatabase.driver(URI, auth=(USER, PASSWORD))

    async with driver.session() as session:
        # Step 1: Find the user ID
        result = await session.run("MATCH (u:User) RETURN u.id AS id LIMIT 5")
        users = await result.data()
        print(f"Found users: {[u['id'] for u in users]}")
        
        if not users:
            print("No users found!")
            return
        
        user_id = users[0]['id']
        print(f"Using user: {user_id}")
        
        # Step 2: See current STUDIED relationships
        result = await session.run("""
            MATCH (u:User {id: $uid})-[r:STUDIED]->(t:Topic)
            RETURN t.name AS topic, r.strength AS strength, r.last_reviewed AS last_reviewed
            ORDER BY r.strength DESC
            LIMIT 10
        """, uid=user_id)
        records = await result.data()
        print(f"\nTop 10 topics by strength:")
        for r in records:
            print(f"  {r['topic']}: strength={r['strength']}")
        
        # Step 3: RESET all negative strengths to 0
        result = await session.run("""
            MATCH (u:User {id: $uid})-[r:STUDIED]->(t:Topic)
            WHERE r.strength < 0
            SET r.strength = 0.0
            RETURN count(r) AS fixed
        """, uid=user_id)
        fixed = await result.data()
        print(f"\n✅ Reset {fixed[0]['fixed']} negative-strength topics to 0")
        
        # Step 4: Set some topics as MASTERED (strength >= 3.0, recently reviewed)
        mastered_topics = ["projectile-motion", "mole-concept", "thermodynamics-process"]
        for topic in mastered_topics:
            await session.run("""
                MATCH (u:User {id: $uid})-[r:STUDIED]->(t:Topic {name: $topic})
                SET r.strength = 4.0, r.correct_count = 6, r.incorrect_count = 1, r.last_reviewed = datetime()
            """, uid=user_id, topic=topic)
        print(f"✅ Set {len(mastered_topics)} topics as MASTERED (strength=4.0)")
        
        # Step 5: Set some topics as DUE (decent strength, but reviewed 5 days ago)
        due_topics = ["electric-flux-and-gauss-law", "collision", "photoelectric-effect"]
        for topic in due_topics:
            await session.run("""
                MATCH (u:User {id: $uid})-[r:STUDIED]->(t:Topic {name: $topic})
                SET r.strength = 2.0, r.correct_count = 3, r.incorrect_count = 2,
                    r.last_reviewed = datetime() - duration({days: 5})
            """, uid=user_id, topic=topic)
        print(f"✅ Set {len(due_topics)} topics as DUE (strength=2.0, reviewed 5 days ago)")
        
        # Step 6: Verify the final state
        result = await session.run("""
            MATCH (u:User {id: $uid})-[r:STUDIED]->(t:Topic)
            WITH t.name AS topic, r.strength AS strength,
                 duration.between(r.last_reviewed, datetime()).days AS days,
                 CASE WHEN r.strength > 0.1 THEN r.strength ELSE 0.1 END AS safe_strength
            WITH topic, strength, days,
                 exp(-1.0 * days / safe_strength) AS retention
            RETURN topic, strength, days, retention
            ORDER BY retention ASC
            LIMIT 20
        """, uid=user_id)
        records = await result.data()
        print(f"\n📊 Topics with lowest retention:")
        for r in records:
            status = "MASTERED" if r['strength'] >= 3.0 and r['retention'] >= 0.7 else \
                     "DUE" if r['strength'] >= 1.5 and r['retention'] < 0.7 else \
                     "WEAK" if r['strength'] < 1.5 else "WEAK"
            print(f"  {r['topic']}: str={r['strength']:.1f}, days={r['days']}, ret={r['retention']:.3f} → {status}")

    await driver.close()
    print("\n🎉 Neo4j data reset complete! Refresh the retention dashboard.")

asyncio.run(main())
