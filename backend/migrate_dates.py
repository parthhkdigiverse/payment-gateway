import asyncio
from database import get_database
from datetime import datetime

async def migrate_dates():
    db = get_database()
    cursor = db.payments.find({})
    count = 0
    async for p in cursor:
        created = p.get('created', '')
        if ' by ' in created:
            # Format is likely "2024-05-12 by Merchant Name"
            date_part = created.split(' by ')[0]
            # Try to get timestamp to reconstruct time, otherwise just use current time or 00:00:00
            ts = p.get('creation_timestamp')
            if ts:
                new_date = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            else:
                new_date = f"{date_part} 00:00:00"
            
            await db.payments.update_one(
                {'_id': p['_id']},
                {'$set': {'created': new_date}}
            )
            count += 1
    print(f"Migrated {count} records to new date format.")

if __name__ == "__main__":
    asyncio.run(migrate_dates())
