import asyncio
from database import get_database

async def check():
    db = get_database()
    p = await db.payments.find_one({'id': 'LNK-101'})
    if p:
        # Avoid rupee symbol in print
        safe_p = {k: str(v).replace('\u20b9', 'Rs.') for k, v in p.items()}
        print(f"Record keys: {list(p.keys())}")
        print(f"ID: '{p.get('id')}'")
        print(f"Status: '{p.get('status')}'")
    else:
        print("Payment not found")

if __name__ == "__main__":
    asyncio.run(check())
