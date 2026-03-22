import asyncio
import os
import sys

sys.path.append(os.getcwd())
from app.core.neo4j_db import connect_to_neo4j, close_neo4j_connection, get_neo4j_driver

async def run():
    print("Connecting Neo4j...")
    try:
        await connect_to_neo4j()
        driver = get_neo4j_driver()
        async with driver.session() as session:
            result = await session.run("RETURN 1 AS num")
            record = await result.single()
            print("Neo4j ping returned:", record["num"])
        await close_neo4j_connection()
        print("Connection Success!")
    except Exception as e:
        print("Connection Failed:", e)

asyncio.run(run())
