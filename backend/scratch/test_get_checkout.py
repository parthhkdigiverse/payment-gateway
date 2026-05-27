import asyncio
import os
from dotenv import load_dotenv
from database import get_database
from main import get_checkout_payment

load_dotenv()

async def test_checkout():
    db = get_database()
    payment = await db.payments.find_one({})
    if not payment:
        print("No payments found in the database to test!")
        return True
        
    payment_id = payment.get("id")
    print(f"Testing public checkout endpoint for payment ID: {payment_id}")
    
    result = await get_checkout_payment(payment_id)
    
    from bson import ObjectId
    for key, value in result.items():
        if isinstance(value, ObjectId):
            print(f"Error: Field '{key}' is a raw ObjectId!")
            return False
            
    print(f"Checkout key keys: {list(result.keys())}")
    print(f"user_id value: {result.get('user_id')} (type: {type(result.get('user_id'))})")
    print("\nSuccess: Checkout endpoint serialized perfectly!")
    return True

if __name__ == "__main__":
    asyncio.run(test_checkout())
