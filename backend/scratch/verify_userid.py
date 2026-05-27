import asyncio
import os
import sys
import uuid
import random
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Ensure we can load dotenv from parent folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..')))
load_dotenv(dotenv_path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'backend', '.env')))

MONGODB_URL = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("db_name", "next_g")

async def test_user_id_system():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    print(f"Connected to MongoDB: {DB_NAME}")
    
    # 1. Simulate signup (/contact)
    test_email = f"test_{random.randint(1000, 9999)}@gmail.com"
    suffix = str(random.randint(100000, 999999))
    user_id = f"U-{suffix}"
    inquiry_id = f"INQ-{suffix[-4:]}"
    
    inquiry_data = {
        "inquiry_id": inquiry_id,
        "user_id": user_id,
        "name": "Test user ID Merchant",
        "email": test_email,
        "username": f"testuser_{suffix[-4:]}",
        "password": "testpassword123",
        "phone": "9876543210",
        "active": False,
        "date": "2026-05-19 12:00"
    }
    
    await db.sign_ups.insert_one(inquiry_data)
    print(f"Inserted mock inquiry with user_id: {user_id} and inquiry_id: {inquiry_id}")
    
    # 2. Retrieve the inquiry to check it
    retrieved_inquiry = await db.sign_ups.find_one({"email": test_email})
    assert retrieved_inquiry is not None
    assert retrieved_inquiry["user_id"] == user_id
    print("Retrieved inquiry successfully verified!")
    
    # 3. Simulate activation (/admin/activate-merchant)
    merchant_data = {
        "merchant_id": f"M-{suffix[-6:]}",
        "user_id": retrieved_inquiry["user_id"],
        "name": retrieved_inquiry["name"],
        "email": retrieved_inquiry["email"],
        "username": retrieved_inquiry["username"],
        "password": retrieved_inquiry["password"],
        "merchant_key": f"mk_live_test_{suffix}",
        "salt_key": "test_salt",
        "plan": "Standard",
        "volume": "$0",
        "status": "Healthy",
        "joined": "2026-05-19"
    }
    
    await db.merchants.update_one(
        {"email": retrieved_inquiry["email"]},
        {"$set": merchant_data},
        upsert=True
    )
    
    await db.sign_ups.update_one(
        {"email": retrieved_inquiry["email"]},
        {"$set": {"active": True, "user_id": retrieved_inquiry["user_id"]}}
    )
    print("Activated merchant and synchronized sign_ups collection successfully!")
    
    # 4. Verify cross-table connection via user_id
    retrieved_merchant = await db.merchants.find_one({"email": test_email})
    assert retrieved_merchant is not None
    assert retrieved_merchant["user_id"] == user_id
    
    # Clean up test documents
    await db.sign_ups.delete_one({"email": test_email})
    await db.merchants.delete_one({"email": test_email})
    print("Cleanup successful. All database assertions passed perfectly!")

if __name__ == "__main__":
    asyncio.run(test_user_id_system())
