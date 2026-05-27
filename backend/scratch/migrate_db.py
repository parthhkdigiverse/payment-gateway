import asyncio
import os
import random
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("db_name", "next_g")

async def migrate():
    print(f"Connecting to database: {DB_NAME}")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    # 1. Migrate Merchants
    print("\n--- Migrating Merchants ---")
    async for m in db.merchants.find({}):
        email = m.get("email")
        current_uid = m.get("user_id")
        
        # We need user_id to be a native BSON ObjectId
        if not isinstance(current_uid, ObjectId):
            new_uid = ObjectId()
            if isinstance(current_uid, str) and len(current_uid) == 24:
                try:
                    new_uid = ObjectId(current_uid)
                except:
                    pass
            elif m.get("role") == "admin":
                # For admin, keep it unique or generate one
                new_uid = ObjectId()
            
            print(f"Merchant {email}: Setting user_id to native ObjectId {new_uid}")
            await db.merchants.update_one({"_id": m["_id"]}, {"$set": {"user_id": new_uid}})
            
    # Load all merchant emails to user_id mapping
    email_to_uid = {}
    async for m in db.merchants.find({}):
        email = m.get("email")
        if email and "user_id" in m:
            email_to_uid[email.lower()] = m["user_id"]
            
    # 2. Migrate Sign Ups
    print("\n--- Migrating Sign Ups ---")
    async for s in db.sign_ups.find({}):
        email = s.get("email")
        current_uid = s.get("user_id")
        
        target_uid = None
        if email and email.lower() in email_to_uid:
            target_uid = email_to_uid[email.lower()]
        elif isinstance(current_uid, ObjectId):
            target_uid = current_uid
        else:
            if isinstance(current_uid, str) and len(current_uid) == 24:
                try:
                    target_uid = ObjectId(current_uid)
                except:
                    pass
            if not target_uid:
                target_uid = ObjectId()
                
        print(f"Sign Up {email}: Setting user_id to native ObjectId {target_uid}")
        await db.sign_ups.update_one({"_id": s["_id"]}, {"$set": {"user_id": target_uid}})
        if email:
            email_to_uid[email.lower()] = target_uid

    # Helper function to resolve user_id for an email or name
    def get_uid_for_email(email_str):
        if not email_str:
            return ObjectId()
        email_str = email_str.lower().strip()
        if email_str in email_to_uid:
            return email_to_uid[email_str]
        # Generate new ObjectId and cache it
        new_uid = ObjectId()
        email_to_uid[email_str] = new_uid
        return new_uid

    # 3. Migrate Payments
    print("\n--- Migrating Payments ---")
    async for p in db.payments.find({}):
        email = p.get("email")
        uid = get_uid_for_email(email)
        print(f"Payment {p.get('id') or p.get('_id')}: Setting user_id to native ObjectId {uid}")
        await db.payments.update_one({"_id": p["_id"]}, {"$set": {"user_id": uid}})

    # 4. Migrate Invites
    print("\n--- Migrating Invites ---")
    if "invites" in await db.list_collection_names():
        async for inv in db.invites.find({}):
            email = inv.get("email")
            uid = get_uid_for_email(email)
            print(f"Invite {inv.get('invite_id')}: Setting user_id to native ObjectId {uid}")
            await db.invites.update_one({"_id": inv["_id"]}, {"$set": {"user_id": uid}})

    # 5. Migrate Tickets
    print("\n--- Migrating Tickets ---")
    async for t in db.tickets.find({}):
        merchant_name = t.get("merchant")
        # Try to resolve merchant_name to an email
        uid = None
        if merchant_name:
            merchant_name_lower = merchant_name.lower().strip()
            # Try to match existing merchant name, email or username
            m = await db.merchants.find_one({
                "$or": [
                    {"name": {"$regex": f"^{merchant_name}$", "$options": "i"}},
                    {"email": {"$regex": f"^{merchant_name}$", "$options": "i"}},
                    {"username": {"$regex": f"^{merchant_name}$", "$options": "i"}}
                ]
            })
            if m and "user_id" in m:
                uid = m["user_id"]
            else:
                uid = get_uid_for_email(merchant_name)
        if not uid:
            uid = ObjectId()
        print(f"Ticket {t.get('id')}: Setting user_id to native ObjectId {uid}")
        await db.tickets.update_one({"_id": t["_id"]}, {"$set": {"user_id": uid}})

    # 6. Migrate Customers
    print("\n--- Migrating Customers ---")
    if "customers" in await db.list_collection_names():
        async for c in db.customers.find({}):
            email = c.get("merchant_email") or c.get("email")
            uid = get_uid_for_email(email)
            print(f"Customer {c.get('id')}: Setting user_id to native ObjectId {uid}")
            await db.customers.update_one({"_id": c["_id"]}, {"$set": {"user_id": uid}})

    # 7. Migrate Logs
    print("\n--- Migrating Logs ---")
    async for l in db.logs.find({}):
        user = l.get("user")
        uid = None
        if user:
            # Check if user is an email
            if "@" in user:
                uid = get_uid_for_email(user)
            else:
                # Try finding merchant by username
                m = await db.merchants.find_one({"username": {"$regex": f"^{user}$", "$options": "i"}})
                if m and "user_id" in m:
                    uid = m["user_id"]
                else:
                    uid = get_uid_for_email(user)
        if not uid:
            uid = ObjectId()
        print(f"Log {l.get('id')}: Setting user_id to native ObjectId {uid}")
        await db.logs.update_one({"_id": l["_id"]}, {"$set": {"user_id": uid}})

    print("\nMigration completed successfully!")

if __name__ == "__main__":
    asyncio.run(migrate())
