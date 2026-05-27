from database import get_database
import asyncio

async def check():
    db = get_database()
    m = await db.merchants.find_one({"email": {"$regex": "tirth", "$options": "i"}})
    if m:
        print(f"Email: |{m['email']}|")
        print(f"Password: |{m['password']}|")
    else:
        print("Merchant not found")

if __name__ == "__main__":
    asyncio.run(check())
