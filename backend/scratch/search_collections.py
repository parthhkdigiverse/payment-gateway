import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
MONGODB_URL = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("db_name", "next_g")

async def get_collections():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    collections = await db.list_collection_names()
    print("Database collections:", collections)
    
    # Check if there are any documents in merchants with role="admin"
    merchants = await db.merchants.find({"role": "admin"}).to_list(length=100)
    print("Merchants with role='admin':", merchants)
    
    # Check if there's any admins collection
    if "admins" in collections:
        admins = await db.admins.find({}).to_list(length=100)
        print("Admins in collection:", admins)

asyncio.run(get_collections())
