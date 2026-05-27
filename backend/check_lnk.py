import asyncio
from database import get_database

async def check():
    db = get_database()
    p = await db.payments.find_one({'id': 'LNK-270'})
    if p:
        from main import add_payment_links
        p = add_payment_links(p)
        print(f"ID: {p.get('id')}")
        print(f"Status: {p.get('status')}")
        print(f"QR Link: {p.get('qr_link')}")
    else:
        print("Payment not found")

if __name__ == "__main__":
    asyncio.run(check())
