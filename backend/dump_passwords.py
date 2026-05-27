from database import get_database
import asyncio

async def dump():
    db = get_database()
    merchants = await db.merchants.find({}, {"name": 1, "email": 1, "password": 1}).to_list(length=100)
    for m in merchants:
        print(f"Name: {m.get('name')}, Email: {m.get('email')}, Password: {m.get('password')}")

if __name__ == "__main__":
    asyncio.run(dump())
