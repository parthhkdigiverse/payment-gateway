import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("db_name", "next_g")

async def check_merchants():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    print("\nChecking specifically for tirth@gmail.com...")
    tirth = await db.sign_ups.find_one({"email": "tirth@gmail.com"})
    print(f"Sign up: {tirth}")
    
    tirth_m = await db.merchants.find_one({"email": "tirth@gmail.com"})
    print(f"Merchant: {tirth_m}")

if __name__ == "__main__":
    asyncio.run(check_merchants())
