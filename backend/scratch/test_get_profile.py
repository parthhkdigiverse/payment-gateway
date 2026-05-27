import asyncio
import os
from dotenv import load_dotenv
from database import get_database
from main import get_merchant_profile

load_dotenv()

async def test_profile():
    # Mock current user session
    current_user = {
        "email": "kh@gmail.com",
        "role": "merchant"
    }
    
    print("Simulating get_merchant_profile call for merchant:")
    profile = await get_merchant_profile(current_user)
    
    print("\nReturned Profile Document:")
    print(profile)
    
    # Verify that there are no non-serializable fields (like ObjectId) in the returned dict
    from bson import ObjectId
    for key, value in profile.items():
        if isinstance(value, ObjectId):
            print(f"Error: Field '{key}' is a raw ObjectId!")
            return False
            
    print("\nSuccess: Profile serialized perfectly!")
    return True

if __name__ == "__main__":
    asyncio.run(test_profile())
