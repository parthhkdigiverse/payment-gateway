import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("db_name", "next_g")

# Create a MongoDB client
client = AsyncIOMotorClient(MONGODB_URL)
db = client[DB_NAME]

async def check_db_connection():
    try:
        # The ping command is cheap and does not require auth.
        await client.admin.command('ping')
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

# Dependency to get the database
def get_database():
    return db

