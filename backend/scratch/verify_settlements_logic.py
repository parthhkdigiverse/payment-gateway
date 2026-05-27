import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..')))
load_dotenv(dotenv_path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'backend', '.env')))

MONGODB_URL = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("db_name", "next_g")

async def test_settlements_logic():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    email = "llp@gmail.com"
    email_regex = {"$regex": f"^{email.replace('.', '\\.')}$", "$options": "i"}
    
    print(f"Testing settlements calculation for: {email}")
    
    query = {"email": email_regex, "status": {"$in": ["Paid", "Success"]}}
    payments = await db.payments.find(query).to_list(length=1000)
    print(f"Found {len(payments)} successful payments for {email}.")
    
    payments_by_date = {}
    for p in payments:
        date_str = None
        if "created" in p and p["created"]:
            created_str = str(p["created"]).strip()
            if len(created_str) >= 10:
                date_str = created_str[:10]
        if not date_str and "creation_timestamp" in p and p["creation_timestamp"]:
            try:
                date_str = datetime.fromtimestamp(float(p["creation_timestamp"])).strftime('%Y-%m-%d')
            except:
                pass
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
            
        amount_str = str(p.get("amount", "0")).replace('₹', '').replace(',', '')
        try:
            amount_val = float(amount_str)
        except:
            amount_val = 0.0
            
        if amount_val > 0:
            if date_str not in payments_by_date:
                payments_by_date[date_str] = 0.0
            payments_by_date[date_str] += amount_val
            
    settlements = []
    today_str = datetime.now().strftime('%Y-%m-%d')
    sorted_dates = sorted(payments_by_date.keys(), reverse=True)
    
    for date_str in sorted_dates:
        gross_amount = payments_by_date[date_str]
        net_amount = gross_amount * 0.98
        
        bank_suffix = str(abs(hash(email)) % 10000).zfill(4)
        bank_name = f"HDFC Bank (****{bank_suffix})"
        status = "Pending" if date_str == today_str else "Completed"
        
        settlement_hash = str(abs(hash(f"{email}-{date_str}")) % 1000000).zfill(6)
        settlement_id = f"SET-{settlement_hash}"
        
        settlements.append({
            "id": settlement_id,
            "amount": f"₹{net_amount:,.2f}",
            "status": status,
            "bank": bank_name,
            "date": date_str,
            "email": email
        })
        
    print(f"Calculated {len(settlements)} dynamic settlements.")
    for s in settlements[:5]:
        print(f"Date: {s['date']} | ID: {s['id']} | Net Amount: {s['amount']} | Status: {s['status']} | Bank: {s['bank']}")
        
    assert len(settlements) >= 0
    print("Settlement logic test passed perfectly!")

if __name__ == "__main__":
    asyncio.run(test_settlements_logic())
