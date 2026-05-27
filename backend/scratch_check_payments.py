import asyncio
from database import get_database

async def main():
    db = get_database()
    p = await db.payments.find_one()
    if p:
        print(f"Keys: {p.keys()}")
        print(f"ID: {p.get('id')}")
        print(f"Name: {p.get('name')}")
    else:
        print("No payments found")

if __name__ == "__main__":
    asyncio.run(main())
