import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("db_name", "next_g")

async def dump_all():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    collections = await db.list_collection_names()
    print(f"Collections in database: {collections}")
    
    for coll_name in collections:
        doc = await db[coll_name].find_one({})
        print(f"\n--- Collection: {coll_name} ---")
        print(doc)

if __name__ == "__main__":
    asyncio.run(dump_all())
