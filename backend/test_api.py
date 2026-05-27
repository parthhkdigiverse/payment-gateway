import asyncio
from database import get_database
from routes import create_cashfree_order

async def main():
    db = get_database()
    session_id = await create_cashfree_order(
        amount=4.00,
        customer_id="test_customer",
        customer_phone="9999999999",
        customer_email="merchant@payflow.com",
        order_id="test_order_xyz_123"
    )
    print("SESSION ID:", session_id)

asyncio.run(main())
