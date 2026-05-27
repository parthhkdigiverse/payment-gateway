import asyncio
from database import get_database

async def check():
    db = get_database()
    sessions = await db.sessions.find({}).to_list(length=100)
    print(f"Total active sessions: {len(sessions)}")
    for s in sessions:
        print(f"Token: {s.get('token')}, Email: {s.get('email')}, Role: {s.get('role')}")

if __name__ == "__main__":
    asyncio.run(check())
