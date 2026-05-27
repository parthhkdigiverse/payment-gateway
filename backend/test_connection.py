import os, sys
from dotenv import load_dotenv

load_dotenv('.env')

DATABASE_URL = os.getenv('DATABASE_URL')
DB_NAME = os.getenv('db_name', 'next_g')

print(f'[INFO] DATABASE_URL found: {bool(DATABASE_URL)}')
print(f'[INFO] DB Name: {DB_NAME}')
if DATABASE_URL:
    print(f'[INFO] URL (masked): {DATABASE_URL[:40]}...')
else:
    print('[ERROR] No DATABASE_URL found!')
    sys.exit(1)

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

    print('[INFO] Attempting connection to MongoDB Atlas...')
    client = MongoClient(DATABASE_URL, serverSelectionTimeoutMS=10000)
    # Force a real connection
    client.admin.command('ping')
    print('[SUCCESS] MongoDB connection is WORKING!')
    db = client[DB_NAME]
    collections = db.list_collection_names()
    print(f'[INFO] Collections in "{DB_NAME}": {collections}')
    client.close()
except ServerSelectionTimeoutError as e:
    print(f'[ERROR] Connection TIMED OUT: {e}')
    sys.exit(1)
except ConnectionFailure as e:
    print(f'[ERROR] Connection FAILED: {e}')
    sys.exit(1)
except Exception as e:
    print(f'[ERROR] Unexpected error: {type(e).__name__}: {e}')
    sys.exit(1)
