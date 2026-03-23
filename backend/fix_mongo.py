import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def fix_times():
    client = AsyncIOMotorClient("mongodb://root:dbVAazDM1bCFRqVRikzLvbPkcfgGCo0WR2vl97NJZnZG5KMk9tAVvodhBqBsGn7l@168.119.148.180:27017/?directConnection=true")
    db = client["solid4x_db"]
    col = db["mock_tests"]
    
    async for test in col.find({"status": "completed"}):
        times = test.get("student_times", {})
        if not times:
            continue
            
        total_time = sum(times.values())
        print(f"Test {test.get('test_id')}: Original total time = {total_time}s")
        if total_time > 10800:
            scale = 10800 / total_time
            new_times = {k: int(v * scale) for k, v in times.items()}
            
            # Ensure it fits
            total = sum(new_times.values())
            
            await col.update_one(
                {"test_id": test["test_id"]},
                {"$set": {"student_times": new_times}}
            )
            print(f"Fixed test {test['test_id']} from {total_time}s to {total}s")

if __name__ == '__main__':
    asyncio.run(fix_times())
