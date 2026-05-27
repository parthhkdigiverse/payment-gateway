import asyncio
from bson import ObjectId
from database import get_database

async def migrate():
    db = get_database()
    # Find withdrawals where user_id is a string and valid ObjectId
    cursor = db.withdrawals.find({"user_id": {"$type": "string"}})
    docs = await cursor.to_list(length=None)
    updated = 0
    for doc in docs:
        user_id_str = doc.get("user_id")
        if user_id_str and ObjectId.is_valid(user_id_str):
            await db.withdrawals.update_one(
                {"_id": doc["_id"]},
                {"$set": {"user_id": ObjectId(user_id_str)}}
            )
            updated += 1
            
    print(f"Migration completed. Updated {updated} withdrawal documents.")

if __name__ == "__main__":
    asyncio.run(migrate())
