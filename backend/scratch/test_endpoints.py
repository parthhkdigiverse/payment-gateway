import asyncio
from database import get_database
from bson import ObjectId

async def run_tests():
    db = get_database()
    print("Testing DB collections read...")
    
    # 1. Test get_db_user_id_for_email helper
    from main import get_db_user_id_for_email, write_audit_log
    email = "kh@gmail.com"
    uid = await get_db_user_id_for_email(db, email)
    print(f"get_db_user_id_for_email success: {uid} (type: {type(uid)})")
    
    # 2. Test write_audit_log
    await write_audit_log("kh@gmail.com", "Test Action", "Test Target")
    print("write_audit_log success")
    
    # 3. Test payments endpoints logic
    payments = await db.payments.find({}, {"_id": 0}).sort("creation_timestamp", -1).to_list(length=10)
    for p in payments:
        if 'user_id' in p:
            p['user_id'] = str(p['user_id'])
    print(f"Payments serialization check success: {len(payments)} payments checked")
    
    # 4. Test tickets logic
    tickets = await db.tickets.find({}, {"_id": 0}).to_list(length=10)
    for t in tickets:
        if 'user_id' in t:
            t['user_id'] = str(t['user_id'])
    print(f"Tickets serialization check success: {len(tickets)} tickets checked")
    
    # 5. Test customers logic
    customers = await db.customers.find({}, {"_id": 0}).to_list(length=10)
    for c in customers:
        if 'user_id' in c:
            c['user_id'] = str(c['user_id'])
    print(f"Customers serialization check success: {len(customers)} customers checked")
    
    # 6. Test invites logic
    invites = await db.invites.find({}, {"_id": 0}).to_list(length=10)
    for inv in invites:
        if 'user_id' in inv:
            inv['user_id'] = str(inv['user_id'])
    print(f"Invites serialization check success: {len(invites)} invites checked")

    # 7. Test settlements logic
    from main import get_merchant_settlements
    # Let's mock a current_user dict
    class MockUser:
        def __getitem__(self, key):
            if key == "email":
                return "kh@gmail.com"
            if key == "role":
                return "merchant"
            return None
        def get(self, key, default=None):
            if key == "email":
                return "kh@gmail.com"
            if key == "role":
                return "merchant"
            return default
            
    try:
        settlements = await get_merchant_settlements(MockUser())
        print(f"Settlements check success: {len(settlements)} settlements returned")
    except Exception as e:
        print(f"Settlements check FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(run_tests())
