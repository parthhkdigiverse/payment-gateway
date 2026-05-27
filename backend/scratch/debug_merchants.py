import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def check():
    client = AsyncIOMotorClient(os.getenv("DATABASE_URL"))
    db = client[os.getenv("db_name", "next_g")]
    
    inquiries = await db.sign_ups.find({}, {"email": 1}).to_list(1000)
    print(f"Inquiries emails: {[i.get('email') for i in inquiries]}")
    
    merchants = await db.merchants.find({}, {"email": 1}).to_list(1000)
    print(f"Merchants emails: {[m.get('email') for m in merchants]}")

if __name__ == "__main__":
    asyncio.run(check())
