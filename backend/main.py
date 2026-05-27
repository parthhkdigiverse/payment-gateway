import os
import secrets
import string
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import check_db_connection, get_database
import httpx
import socketio

app = FastAPI()

# Socket.IO Setup
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO Events
@sio.event
async def connect(sid, environ):
    print(f"Socket connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Socket disconnected: {sid}")

def generate_secure_key(length=32):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_salt(length=16):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

class Payment(BaseModel):
    name: str
    amount: str
    currency: str = "INR"
    status: str = "Active"
    merchant_name: str = "Luxury Merchant" # Default for now
    upi_id: str = "nexify@okicici" # Default VPA
    custom_qr_link: str = None # Optional custom QR link
    payment_session_id: str = None # Added for Cashfree integration
    order_id: str = None # Optional custom order ID
    return_url: str = None # Optional custom return URL

async def create_cashfree_order(amount: float, customer_id: str, customer_phone: str, customer_email: str, order_id: str = None, return_url: str = None):
    """
    Create an order in Cashfree and return the payment_session_id.
    """
    app_id = os.getenv("CASHFREE_APP_ID")
    secret_key = os.getenv("CASHFREE_SECRET_KEY")
    environment = os.getenv("CASHFREE_ENVIRONMENT", "sandbox")
    
    url = "https://sandbox.cashfree.com/pg/orders" if environment == "sandbox" else "https://api.cashfree.com/pg/orders"
    
    headers = {
        "x-client-id": app_id,
        "x-client-secret": secret_key,
        "x-api-version": "2023-08-01",
        "Content-Type": "application/json"
    }
    
    payload = {
        "order_id": order_id or customer_id,
        "order_amount": amount,
        "order_currency": "INR",
        "customer_details": {
            "customer_id": customer_id,
            "customer_phone": customer_phone or "9999999999", # Cashfree requires a phone
            "customer_email": customer_email
        }
    }
    
    # Use provided return_url or default
    payload["order_meta"] = {
        "return_url": return_url or "http://localhost:3000/payment-success?order_id={order_id}"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get("payment_session_id")
            else:
                print(f"Cashfree Order Error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"Cashfree Request Exception: {e}")
        return None

async def initiate_cashfree_upi_pay(payment_session_id: str):
    """
    Initiate a UPI payment to get the official QR link from Cashfree.
    """
    app_id = os.getenv("CASHFREE_APP_ID")
    secret_key = os.getenv("CASHFREE_SECRET_KEY")
    environment = os.getenv("CASHFREE_ENVIRONMENT", "sandbox")
    
    # Correct endpoint for Order Pay in v3
    url = "https://sandbox.cashfree.com/pg/orders/sessions" if environment == "sandbox" else "https://api.cashfree.com/pg/orders/sessions"
    
    headers = {
        "x-client-id": app_id,
        "x-client-secret": secret_key,
        "x-api-version": "2023-08-01",
        "Content-Type": "application/json"
    }
    
    payload = {
        "payment_session_id": payment_session_id,
        "payment_method": {
            "upi": {
                "channel": "qrcode"
            }
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # Extract the UPI link (data.data.payload.qrcode or data.data.channel_data.upi_id)
                # In v3 Pay response, it's often in data.data.payload or similar
                return data.get("data", {}).get("payload", {}).get("qrcode") or data.get("data", {}).get("payment_method", {}).get("upi", {}).get("qrcode")
            else:
                print(f"Cashfree Pay Error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"Cashfree Pay Request Exception: {e}")
        return None

def add_payment_links(payment: dict):
    amount = str(payment.get("amount", "0")).replace('₹', '').replace(',', '')
    merchant_name = payment.get("merchant_name", "Merchant")
    payer_name = payment.get("name", "Customer")
    upi_id = payment.get("upi_id", "nexify@okicici")
    
    # Clean up names for URL encoding
    import urllib.parse
    m_name_enc = urllib.parse.quote(merchant_name)
    p_name_enc = urllib.parse.quote(payer_name)
    
    upi_string = f"upi://pay?pa={upi_id}&pn={m_name_enc}&am={amount}&cu=INR&tn=Payment for {p_name_enc}"
    
    # If custom QR link is provided, use it. Otherwise generate one.
    if payment.get("custom_qr_link"):
        qr_link = payment.get("custom_qr_link")
    else:
        qr_link = f"https://api.qrserver.com/v1/create-qr-code/?size=600x600&data={urllib.parse.quote(upi_string)}"
    
    # Log the QR link in the backend console for visibility
    print(f"\n[BACKEND] QR Code Link for {payment.get('id', 'Unknown')}:")
    print(f"{qr_link}\n")
    
    payment["upi_string"] = upi_string
    payment["qr_link"] = payment.get("qr_link") or qr_link
    payment["checkout_url"] = payment.get("checkout_url") or f"http://localhost:3000/checkout/{payment.get('id')}"
    payment["cf_environment"] = os.getenv("CASHFREE_ENVIRONMENT", "sandbox")
    return payment

class ContactInquiry(BaseModel):
    name: str
    phone: str
    email: str
    username: str

class MerchantProfile(BaseModel):
    name: str
    email: str

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@app.get("/")
async def root():
    return {"message": "Backend is running"}

@app.post("/login")
async def login(req: LoginRequest):
    db = get_database()
    email = req.email.strip()
    password = req.password.strip()
    
    # Check if merchant exists with this email and password
    merchant = await db.merchants.find_one({"email": email, "password": password})
    
    if merchant:
        return {"status": "success", "message": "Login successful"}
    
    # Check for the default merchant if not in DB yet
    if email == "merchant@payflow.com" and password == "password123":
        return {"status": "success", "message": "Login successful"}
    
    # Check for the default admin
    if email == "admin@payflow.com" and password == "admin123":
        return {"status": "success", "message": "Login successful"}
        
    return {"status": "error", "message": "Invalid email or password"}


@app.post("/contact")
async def create_contact(inquiry: ContactInquiry):
    from datetime import datetime
    db = get_database()
    inquiry_data = inquiry.dict()
    inquiry_data["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    inquiry_data["active"] = False  # Must be activated by admin
    
    # Insert the inquiry only
    result = await db.sign_ups.insert_one(inquiry_data)
    
    return {"status": "success", "id": str(result.inserted_id), "message": "Application submitted for review"}


@app.get("/merchant/profile")
async def get_profile():
    db = get_database()
    # For now, we fetch a default merchant or the first one
    profile = await db.merchants.find_one({}, {"_id": 0})
    if not profile:
        return {
            "name": "Luxury Merchant", 
            "email": "merchant@payflow.com",
            "merchant_key": "mk_live_default_key_123456",
            "salt_key": "salt_default_123"
        }
    return profile

@app.post("/merchant/profile")
async def update_profile(profile: MerchantProfile):
    db = get_database()
    await db.merchants.update_one(
        {}, # Update the first/only merchant for now
        {"$set": profile.dict()},
        upsert=True
    )
    return {"status": "success"}

@app.post("/merchant/password")
async def update_password(update: PasswordUpdate):
    db = get_database()
    # In a real app, verify current_password first
    await db.merchants.update_one(
        {},
        {"$set": {"password": update.new_password}},
        upsert=True
    )
    return {"status": "success"}

@app.post("/merchant/regenerate-keys")
async def regenerate_keys():
    db = get_database()
    new_merchant_key = f"mk_live_{generate_secure_key()}"
    new_salt_key = generate_salt()
    
    await db.merchants.update_one(
        {}, # Update the first/only merchant for now
        {"$set": {
            "merchant_key": new_merchant_key,
            "salt_key": new_salt_key
        }}
    )
    return {
        "status": "success", 
        "merchant_key": new_merchant_key, 
        "salt_key": new_salt_key
    }

@app.get("/db-check")
async def db_check():
    is_connected = await check_db_connection()
    if is_connected:
        return {"status": "success", "message": "Database is connected"}
    else:
        return {"status": "error", "message": "Database connection failed"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
@app.get("/admin/merchants")
async def get_all_merchants():
    db = get_database()
    merchants = await db.merchants.find({}, {"_id": 0}).to_list(length=100)
    return merchants

@app.get("/admin/inquiries")
async def get_all_inquiries():
    db = get_database()
    inquiries = []
    async for doc in db.sign_ups.find({}):
        doc['id'] = str(doc['_id'])
        # Keep original inquiry_id if it exists, otherwise use the stringified _id
        if 'inquiry_id' not in doc:
            doc['inquiry_id'] = doc['id']
        del doc['_id']
        inquiries.append(doc)
    return inquiries

@app.get("/admin/logs")
async def get_all_logs():
    db = get_database()
    logs = await db.logs.find({}, {"_id": 0}).to_list(length=100)
    return logs

@app.get("/admin/tickets")
async def get_all_tickets():
    db = get_database()
    tickets = await db.tickets.find({}, {"_id": 0}).to_list(length=100)
    return tickets

@app.get("/admin/stats")
async def get_admin_stats():
    db = get_database()
    merchant_count = await db.merchants.count_documents({})
    inquiry_count = await db.sign_ups.count_documents({"active": {"$ne": True}})
    ticket_count = await db.tickets.count_documents({"status": "Open"})
    
    return {
        "merchants": merchant_count,
        "new_inquiries": inquiry_count,
        "open_tickets": ticket_count,
        "total_volume": "$6.5M" # Static for now
    }

class ActivateRequest(BaseModel):
    inquiry_id: str
    password: str

@app.post("/admin/activate-merchant")
async def activate_merchant(req: ActivateRequest):
    if len(req.password) < 12:
        return {"status": "error", "message": "Password must be at least 12 characters long"}
        
    db = get_database()
    from datetime import datetime
    
    # 1. Find the inquiry
    inquiry = await db.sign_ups.find_one({"inquiry_id": req.inquiry_id})
    if not inquiry:
        # Try finding by mongo _id if inquiry_id is missing
        from bson import ObjectId
        try:
            inquiry = await db.sign_ups.find_one({"_id": ObjectId(req.inquiry_id)})
        except:
            return {"status": "error", "message": "Inquiry not found"}
            
    if not inquiry:
        return {"status": "error", "message": "Inquiry not found"}

    # 2. Create a merchant from inquiry
    inq_id_part = inquiry.get('inquiry_id', '0000')
    # Clean up the ID part to get only digits or last 4 chars
    suffix = ''.join(filter(str.isdigit, inq_id_part))[-4:] or inq_id_part[-4:]
    
    merchant_data = {
        "merchant_id": f"M-{suffix}",
        "name": inquiry['name'],
        "email": inquiry['email'],
        "password": req.password,
        "merchant_key": f"mk_live_{generate_secure_key()}",
        "salt_key": generate_salt(),
        "plan": "Standard", # Default
        "volume": "$0",
        "status": "Healthy",
        "joined": datetime.now().strftime("%Y-%m-%d")
    }
    
    # Insert or Update merchant
    await db.merchants.update_one(
        {"email": inquiry['email']},
        {"$set": merchant_data},
        upsert=True
    )
    
    # 3. Mark inquiry as active
    await db.sign_ups.update_one(
        {"email": inquiry['email']},
        {"$set": {"active": True}}
    )
    
    return {"status": "success", "message": "Merchant activated"}

@app.get("/merchant/payments")
async def get_payments():
    db = get_database()
    payments = await db.payments.find({}, {"_id": 0}).to_list(length=100)
    return [add_payment_links(p) for p in payments]

@app.get("/merchant/payments/{payment_id}")
async def get_payment(payment_id: str):
    db = get_database()
    # Try finding by 'id' field first
    payment = await db.payments.find_one({"id": payment_id}, {"_id": 0})
    
    # Fallback: Try finding by name (if id was somehow lost or mismatched)
    if not payment:
        payment = await db.payments.find_one({"name": payment_id}, {"_id": 0})
        
    if not payment:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Payment link not found")
    return add_payment_links(payment)

@app.post("/merchant/verify-utr")
async def verify_utr(req: dict):
    db = get_database()
    utr = req.get("utr")
    payment_id = req.get("payment_id")
    
    if not utr or not payment_id:
        return {"status": "error", "message": "Missing UTR or payment_id"}
        
    # Update the payment with the UTR
    result = await db.payments.update_one(
        {"id": payment_id},
        {"$set": {"utr_id": utr}}
    )
    
    if result.modified_count > 0:
        # Notify via Socket.IO
        await sio.emit("payment_update", {
            "type": "UTR_SUBMITTED",
            "payment_id": payment_id,
            "utr": utr,
            "message": f"New UTR submitted for {payment_id}",
            "redirect_url": f"/merchant/payments"
        })
        return {"status": "success", "message": "UTR verified and saved successfully"}
    else:
        # Check if it was already set or if the record doesn't exist
        existing = await db.payments.find_one({"id": payment_id})
        if existing:
            return {"status": "success", "message": "UTR already submitted"}
        return {"status": "error", "message": "Payment record not found"}

@app.post("/merchant/payments")
async def create_payment(payment: Payment):
    from datetime import datetime
    import random
    db = get_database()
    payment_data = payment.dict()
    
    # Get merchant name for the link
    merchant = await db.merchants.find_one({}, {"name": 1})
    m_name = merchant["name"] if merchant else "Luxury Merchant"
    
    # Use provided order_id or generate one
    payment_data["id"] = payment_data.get("order_id") or f"LNK-{random.randint(100, 999)}"
    payment_data["merchant_name"] = m_name
    payment_data["created"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    payment_data["creation_timestamp"] = datetime.now().timestamp()
    
    # Create Cashfree Order
    amount_val = float(str(payment_data["amount"]).replace('₹', '').replace(',', ''))
    session_id = await create_cashfree_order(
        amount=amount_val,
        customer_id=f"CUST-{random.randint(1000, 9999)}",
        customer_phone="9999999999", # Placeholder
        customer_email="customer@example.com", # Placeholder
        order_id=payment_data["id"],
        return_url=payment_data.get("return_url")
    )
    
    if session_id:
        payment_data["payment_session_id"] = session_id
        print(f"Created Cashfree Session: {session_id}")
        
        # New: Initiate Pay to get the official UPI Link
        cf_upi_link = await initiate_cashfree_upi_pay(session_id)
        if cf_upi_link:
            payment_data["cf_upi_link"] = cf_upi_link
            print(f"Stored Cashfree UPI Link: {cf_upi_link}")
    
    # Pre-calculate and store links permanently
    payment_data = add_payment_links(payment_data)
    
    await db.payments.insert_one(payment_data)
    if "_id" in payment_data: del payment_data["_id"]
    
    # Notify via Socket.IO
    await sio.emit("payment_update", {
        "type": "PAYMENT_CREATED",
        "payment_id": payment_data["id"],
        "message": f"New payment page created: {payment_data['name']}",
        "redirect_url": f"/merchant/payments"
    })
    
    return {"status": "success", "payment": payment_data}

@app.post("/webhook/cashfree")
async def cashfree_webhook(payload: dict):
    """
    Handle Cashfree webhooks for payment success.
    """
    event_type = payload.get("type")
    
    if event_type == "PAYMENT_SUCCESS_WEBHOOK":
        data = payload.get("data", {})
        order_info = data.get("order", {})
        payment_info = data.get("payment", {})
        
        order_id = order_info.get("order_id")
        payment_status = payment_info.get("payment_status")
        
        if order_id and payment_status == "SUCCESS":
            db = get_database()
            
            # Update the payment status in the database
            # We look for order_id in our 'id' field
            result = await db.payments.update_one(
                {"id": order_id},
                {"$set": {
                    "status": "Paid",
                    "cf_payment_id": payment_info.get("cf_payment_id"),
                    "payment_time": payment_info.get("payment_time"),
                    "payment_method": payment_info.get("payment_group")
                }}
            )
            
            if result.modified_count > 0:
                print(f"Successfully updated payment {order_id} to Paid")
                
                # Notify via Socket.IO
                await sio.emit("payment_update", {
                    "type": "PAYMENT_PAID",
                    "order_id": order_id,
                    "message": f"Payment Successful for Order: {order_id}",
                    "redirect_url": f"/merchant/payments"
                })
                
                return {"status": "success", "message": "Payment updated"}
            else:
                # Check if it was already Paid
                existing = await db.payments.find_one({"id": order_id})
                if existing:
                    if existing.get("status") == "Paid":
                        print(f"Payment {order_id} was already marked as Paid")
                        return {"status": "success", "message": "Payment already processed"}
                    else:
                        print(f"Payment {order_id} found but not updated (unknown reason)")
                        return {"status": "error", "message": "Payment found but update failed"}
                
                print(f"Payment {order_id} not found in database")
                return {"status": "error", "message": "Payment not found"}
                
    return {"status": "ignored", "message": "Event type not handled or invalid"}
