import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv('.env')

DATABASE_URL = os.getenv('DATABASE_URL')
DB_NAME = os.getenv('db_name', 'next_g')

async def migrate_payments_user_id():
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client[DB_NAME]
    
    print("[INFO] Migrating payments user_id to match merchant _id...")
    payments = await db.payments.find({}).to_list(None)
    modified = 0
    for payment in payments:
        email = payment.get("email")
        if email:
            email_regex = {"$regex": f"^{email.replace('.', '\\.')}$", "$options": "i"}
            merchant = await db.merchants.find_one({"email": email_regex})
            if merchant:
                await db.payments.update_one(
                    {"_id": payment["_id"]},
                    {"$set": {"user_id": merchant["_id"]}}
                )
                modified += 1
    
    print(f"[SUCCESS] Migrated user_id for {modified} payments.")
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate_payments_user_id())
