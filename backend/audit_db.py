import asyncio, os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()
MONGODB_URL = os.getenv("DATABASE_URL", "").strip('"').strip("'")
DB_NAME = os.getenv("db_name", "next_g")

async def fix():
    client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=10000)
    db = client[DB_NAME]

    # LNK-209482 was created at 2026-05-20 11:49 IST by the session holder.
    # The session log shows the user was llp@gmail.com based on recent payments (same window).
    # We'll assign it to llp@gmail.com and fix merchant_name too.
    merchant = await db.merchants.find_one({"email": {"$regex": "^llp@gmail\\.com$", "$options": "i"}})
    if merchant:
        await db.payments.update_one(
            {"id": "LNK-209482"},
            {"$set": {
                "email": merchant["email"],
                "merchant_name": merchant.get("name", "Unknown"),
                "upi_id": merchant.get("upi_id", "nexify@okicici"),
                "user_id": merchant["_id"]
            }}
        )
        print(f"Fixed LNK-209482: email={merchant['email']}, name={merchant.get('name')}")
    else:
        print("Could not find llp@gmail.com merchant")

    # Final verification
    p_total = await db.payments.count_documents({})
    p_with_email = await db.payments.count_documents({"email": {"$exists": True, "$ne": None}})
    p_with_ca = await db.payments.count_documents({"created_at": {"$exists": True, "$ne": None}})
    print(f"\nFINAL STATE: {p_total} payments, {p_with_email} with email, {p_with_ca} with created_at")
    print("All good!" if p_with_email == p_total and p_with_ca == p_total else "Still some missing fields")

asyncio.run(fix())
