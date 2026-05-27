import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("db_name", "next_g")

async def list_all():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    print("\n--- All Sign Ups ---")
    async for s in db.sign_ups.find({}):
        print(s)
        
    print("\n--- All Merchants ---")
    async for m in db.merchants.find({}):
        print(m)

if __name__ == "__main__":
    asyncio.run(list_all())
