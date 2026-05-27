import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv('.env')

DATABASE_URL = os.getenv('DATABASE_URL')
DB_NAME = os.getenv('db_name', 'next_g')

async def remove_user_id():
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client[DB_NAME]
    
    print("[INFO] Removing user_id from merchants collection...")
    result = await db.merchants.update_many({}, {"$unset": {"user_id": ""}})
    print(f"[SUCCESS] Modified {result.modified_count} merchant documents.")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(remove_user_id())
