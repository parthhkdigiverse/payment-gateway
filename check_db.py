import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def check_sessions():
    client = AsyncIOMotorClient(os.getenv("DATABASE_URL"))
    db = client[os.getenv("db_name", "next_g")]
    
    print("--- Sessions ---")
    async for session in db.sessions.find():
        print(session)
    
    print("\n--- Merchants ---")
    async for merchant in db.merchants.find():
        print(merchant)

if __name__ == "__main__":
    asyncio.run(check_sessions())
