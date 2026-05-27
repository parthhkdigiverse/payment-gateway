import asyncio
from database import get_database

async def check():
    db = get_database()
    session = await db.sessions.find_one({"token": "f1d96727-6a4c-4cf3-9e53-6a5b2db4ec8f"})
    if session:
        print(f"FOUND: Token={session.get('token')}, Email={session.get('email')}, Role={session.get('role')}")
    else:
        print("NOT FOUND")

if __name__ == "__main__":
    asyncio.run(check())
