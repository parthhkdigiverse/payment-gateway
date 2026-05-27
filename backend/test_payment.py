import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.getenv("db_name", "next_g")

async def run():
    client = AsyncIOMotorClient(os.getenv("DATABASE_URL"))
    db = client[DB_NAME]
    payment = await db.payments.find_one({})
    if payment:
        print(f"Payment found: {payment.get('id')}")
        print(f"user_id: {payment.get('user_id')}")
        print(f"Checkout url: {payment.get('checkout_url')}")
    else:
        print('No payments')

asyncio.run(run())
