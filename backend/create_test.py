import asyncio
from database import get_database
from datetime import datetime
import random

async def create_test_payment():
    db = get_database()
    payment_id = f"LNK-{random.randint(100, 999)}"
    payment_data = {
        "id": payment_id,
        "name": "Test Payment",
        "amount": "₹1.00",
        "currency": "INR",
        "status": "Active",
        "merchant_name": "Luxury Merchant",
        "created": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "creation_timestamp": datetime.now().timestamp()
    }
    await db.payments.insert_one(payment_data)
    
    from main import add_payment_links
    payment_data = add_payment_links(payment_data)
    
    print(f"Created payment with ID: {payment_id}")
    print(f"QR Link: {payment_data.get('qr_link')}")
    return payment_id

if __name__ == "__main__":
    asyncio.run(create_test_payment())
