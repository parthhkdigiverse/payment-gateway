import asyncio
from database import get_database
from datetime import datetime

async def check_sessions():
    db = get_database()
    count = await db.sessions.count_documents({})
    print(f"Total sessions: {count}")
    async for session in db.sessions.find():
        print(f"Session: token={session.get('token')}, email={session.get('email')}, role={session.get('role')}, created={session.get('created_at')}")

if __name__ == "__main__":
    asyncio.run(check_sessions())
