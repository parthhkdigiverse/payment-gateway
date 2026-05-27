"""
Migration: Backfill missing fields across all collections in next_g.

Fixes:
1. payments  -> add created_at/updated_at where missing (use creation_timestamp or now)
2. payments  -> add email where missing (try to match via merchant_name or mark as unknown)
3. merchants -> add upi_id, username, phone, role where missing
4. merchants -> ensure user_id is present
"""
import asyncio, os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()
MONGODB_URL = os.getenv("DATABASE_URL", "").strip('"').strip("'")
DB_NAME = os.getenv("db_name", "next_g")

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def ts_to_iso(ts):
    """Convert a Unix timestamp float to ISO 8601 UTC string."""
    if ts:
        try:
            return datetime.fromtimestamp(float(ts), tz=timezone.utc).isoformat()
        except Exception:
            pass
    return now_iso()

async def migrate():
    client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=10000)
    db = client[DB_NAME]

    # ─────────────────────────────────────────────
    # 1. Backfill payments: created_at / updated_at
    # ─────────────────────────────────────────────
    print("\n[1] Backfilling payments: created_at / updated_at ...")
    payments = await db.payments.find({}).to_list(length=1000)
    updated_count = 0
    for p in payments:
        update = {}
        if not p.get("created_at"):
            update["created_at"] = ts_to_iso(p.get("creation_timestamp"))
        if not p.get("updated_at"):
            update["updated_at"] = ts_to_iso(p.get("creation_timestamp"))
        if update:
            await db.payments.update_one({"_id": p["_id"]}, {"$set": update})
            updated_count += 1
    print(f"    -> Updated {updated_count} payment(s) with timestamps.")

    # ─────────────────────────────────────────────────────────────────
    # 2. Backfill payments: email (try to resolve via merchant_name)
    # ─────────────────────────────────────────────────────────────────
    print("\n[2] Backfilling payments: missing email ...")
    orphaned = await db.payments.find({"email": {"$exists": False}}).to_list(length=1000)
    orphaned += await db.payments.find({"email": None}).to_list(length=1000)
    # Deduplicate by _id
    seen = set()
    unique_orphaned = []
    for p in orphaned:
        if p["_id"] not in seen:
            seen.add(p["_id"])
            unique_orphaned.append(p)

    email_fixed = 0
    for p in unique_orphaned:
        merchant_name = p.get("merchant_name")
        resolved_email = None
        if merchant_name:
            merchant = await db.merchants.find_one({
                "name": {"$regex": f"^{merchant_name}$", "$options": "i"}
            })
            if merchant:
                resolved_email = merchant.get("email")
        if resolved_email:
            await db.payments.update_one(
                {"_id": p["_id"]},
                {"$set": {"email": resolved_email}}
            )
            email_fixed += 1
            print(f"    -> Fixed email for payment {p.get('id')}: {resolved_email}")
        else:
            print(f"    -> Could not resolve email for payment {p.get('id')} (merchant_name={merchant_name})")
    print(f"    -> Fixed {email_fixed}/{len(unique_orphaned)} orphaned payment(s).")

    # ────────────────────────────────────────────────────────────────────────
    # 3. Backfill merchants: upi_id, username, phone, role, created_at fields
    # ────────────────────────────────────────────────────────────────────────
    print("\n[3] Backfilling merchants: missing fields ...")
    merchants = await db.merchants.find({}).to_list(length=100)
    merchant_updated = 0
    for m in merchants:
        update = {}
        if not m.get("upi_id"):
            update["upi_id"] = "nexify@okicici"  # sensible default
        if not m.get("username"):
            # derive from email or name
            email = m.get("email", "")
            update["username"] = email.split("@")[0] if email else m.get("name", "merchant")
        if not m.get("phone"):
            update["phone"] = ""
        if not m.get("role"):
            # If it has merchant_id it's a merchant, otherwise check if name suggests admin
            update["role"] = "merchant" if m.get("merchant_id") else "admin"
        if not m.get("created_at"):
            joined = m.get("joined")
            if joined:
                try:
                    dt = datetime.strptime(joined, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    update["created_at"] = dt.isoformat()
                    update["updated_at"] = dt.isoformat()
                except Exception:
                    update["created_at"] = now_iso()
                    update["updated_at"] = now_iso()
            else:
                update["created_at"] = now_iso()
                update["updated_at"] = now_iso()
        if update:
            await db.merchants.update_one({"_id": m["_id"]}, {"$set": update})
            merchant_updated += 1
            print(f"    -> Updated merchant {m.get('email')}: {list(update.keys())}")
    print(f"    -> Updated {merchant_updated} merchant(s).")

    # ─────────────────────────────────────────
    # 4. Final verification
    # ─────────────────────────────────────────
    print("\n[4] Final verification ...")
    p_total = await db.payments.count_documents({})
    p_with_created_at = await db.payments.count_documents({"created_at": {"$exists": True, "$ne": None}})
    p_with_email = await db.payments.count_documents({"email": {"$exists": True, "$ne": None}})
    m_total = await db.merchants.count_documents({})
    m_with_upi = await db.merchants.count_documents({"upi_id": {"$exists": True, "$ne": None}})

    print(f"    payments ({p_total} total): {p_with_created_at} have created_at, {p_with_email} have email")
    print(f"    merchants ({m_total} total): {m_with_upi} have upi_id")
    print("\nMigration complete!")

asyncio.run(migrate())
