import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

MONGODB_URL = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("db_name", "next_g")

async def seed():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]

    print(f"Connecting to {DB_NAME}...")

    # Seed Merchants
    merchants = [
        {
            "merchant_id": "M-9021",
            "name": "Luxury Goods Co.",
            "email": "merchant@payflow.com",
            "password": "password123",
            "merchant_key": "mk_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
            "salt_key": "salt_8h7g6f5e4d3c",
            "plan": "Enterprise",
            "volume": "$4.2M",
            "status": "Healthy",
            "joined": "2024-01-15"
        },
        {
            "merchant_id": "M-8842",
            "name": "Global Tech Inc.",
            "email": "tech@global.com",
            "password": "password123",
            "merchant_key": "mk_live_z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4",
            "salt_key": "salt_1a2b3c4d5e6f",
            "plan": "Standard",
            "volume": "$890K",
            "status": "Healthy",
            "joined": "2024-02-10"
        },
        {
            "merchant_id": "M-7731",
            "name": "Eco Systems Ltd.",
            "email": "eco@systems.com",
            "password": "password123",
            "merchant_key": "mk_live_q1w2e3r4t5y6u7i8o9p0a1s2d3f4g5h6",
            "salt_key": "salt_zxcvbnm12345",
            "plan": "Enterprise",
            "volume": "$1.5M",
            "status": "Warning",
            "joined": "2024-03-05"
        },
        {
            "merchant_id": "M-0001",
            "name": "Kenil Merchant",
            "email": "kenilhkdigiverse@gmail.com",
            "password": "password123",
            "merchant_key": "mk_live_k1e2n3i4l5m6e7r8c9h0a1n2t3k4e5y6",
            "salt_key": "salt_kenil_secure",
            "plan": "Enterprise",
            "volume": "$0",
            "status": "Healthy",
            "joined": "2024-05-12"
        },
        {
            "merchant_id": "M-T001",
            "name": "Tirth Merchant",
            "email": "tirth@gmail.com",
            "password": "password123",
            "merchant_key": "mk_live_tirth_secure_key_999",
            "salt_key": "salt_tirth_123",
            "plan": "Enterprise",
            "volume": "$0",
            "status": "Healthy",
            "joined": "2024-05-12"
        }
    ]
    
    await db.merchants.delete_many({})
    await db.merchants.insert_many(merchants)
    print("Seed: Merchants inserted.")

    # Seed Inquiries (Sign ups)
    inquiries = [
        {
            "inquiry_id": "INQ-001",
            "name": "James Wilson",
            "email": "james@wilson.com",
            "phone": "+1 234 567 890",
            "username": "jwilson_dev",
            "date": "2024-05-11 10:15",
            "active": False
        },
        {
            "inquiry_id": "INQ-002",
            "name": "Sophia Chen",
            "email": "sophia@chen-inc.com",
            "phone": "+1 987 654 321",
            "username": "schen_biz",
            "date": "2024-05-11 09:30",
            "active": True
        }
    ]
    await db.sign_ups.delete_many({})
    await db.sign_ups.insert_many(inquiries)
    print("Seed: Inquiries inserted.")

    # Seed Logs
    logs = [
        {
            "id": "LOG-5521",
            "action": "API Key Rotated",
            "user": "System",
            "target": "Luxury Goods Co.",
            "ip": "192.168.1.1",
            "timestamp": "2024-05-11 12:45"
        },
        {
            "id": "LOG-5520",
            "action": "Merchant Login",
            "user": "James Wilson",
            "target": "M-9021",
            "ip": "45.12.33.10",
            "timestamp": "2024-05-11 12:30"
        }
    ]
    await db.logs.delete_many({})
    await db.logs.insert_many(logs)
    print("Seed: Logs inserted.")

    # Seed Tickets
    tickets = [
        {
            "id": "TKT-1002",
            "subject": "Payout Delayed",
            "merchant": "Luxury Goods Co.",
            "priority": "High",
            "status": "Open",
            "created": "2024-05-11 11:00"
        },
        {
            "id": "TKT-1001",
            "subject": "API Integration Issue",
            "merchant": "Global Tech Inc.",
            "priority": "Medium",
            "status": "Pending",
            "created": "2024-05-11 08:00"
        }
    ]
    await db.tickets.delete_many({})
    await db.tickets.insert_many(tickets)
    print("Seed: Tickets inserted.")

    # Seed Payments
    payments = [
        {
            "id": "LNK-101",
            "name": "Consultation Fee",
            "amount": "₹1,500.00",
            "currency": "INR",
            "status": "Active",
            "merchant_name": "Luxury Goods Co.",
            "created": "2024-05-12 by Luxury Goods Co.",
            "creation_timestamp": datetime.now().timestamp()
        },
        {
            "id": "LNK-102",
            "name": "Product Upgrade",
            "amount": "₹5,000.00",
            "currency": "INR",
            "status": "Active",
            "merchant_name": "Global Tech Inc.",
            "created": "2024-05-12 by Global Tech Inc.",
            "creation_timestamp": datetime.now().timestamp()
        }
    ]
    await db.payments.delete_many({})
    await db.payments.insert_many(payments)
    print("Seed: Payments inserted.")

    print("Database seeding completed.")

if __name__ == "__main__":
    asyncio.run(seed())
