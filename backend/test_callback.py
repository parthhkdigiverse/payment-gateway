import asyncio
import json
import urllib.request
from database import get_database
from datetime import datetime

payload = {
  "data": {
    "order": {
      "order_id": "order_OFR_2",
      "order_amount": 2,
      "order_currency": "INR",
      "order_tags": None
    },
    "payment": {
      "cf_payment_id": "1453002795",
      "payment_status": "SUCCESS",
      "payment_amount": 50.0,
      "payment_currency": "INR",
      "payment_message": "00::Transaction success",
      "payment_time": "2025-01-15T12:20:29+05:30",
      "bank_reference": "234928698581",
      "auth_id": None,
      "payment_method": {
        "upi": {
          "channel": "collect",
          "upi_id": "rishab@ybl",
          "upi_instrument": "UPI_CREDIT_CARD",
          "upi_instrument_number": "masked card number",
          "upi_payer_ifsc": "SBI0025434",
          "upi_payer_account_number": "XXXXX0231"
        }
      },
      "payment_group": "upi",
      "international_payment": {
        "international": False
      },
      "payment_surcharge": {
        "payment_surcharge_service_charge": 0.36,
        "payment_surcharge_service_tax": 0.06
      }
    },
    "customer_details": {
      "customer_name": None,
      "customer_id": "7112AAA812234",
      "customer_email": "test@gmail.com",
      "customer_phone": "9908734801"
    },
    "payment_gateway_details": {
      "gateway_name": "CASHFREE",
      "gateway_order_id": "1634766330",
      "gateway_payment_id": "1504280029",
      "gateway_order_reference_id": "abc_124",
      "gateway_settlement": "CASHFREE",
      "gateway_status_code": None
    },
    "payment_offers": [
      {
        "offer_id": "0f05e1d0-fbf8-4c9c-a1f0-814c7b2abdba",
        "offer_type": "DISCOUNT",
        "offer_meta": {
          "offer_title": "50% off on UPI",
          "offer_description": "50% off for testing",
          "offer_code": "UPI50",
          "offer_start_time": "2022-11-09T06:23:25.972Z",
          "offer_end_time": "2025-02-27T18:30:00Z"
        },
        "offer_redemption": {
          "redemption_status": "SUCCESS",
          "discount_amount": 1,
          "cashback_amount": 0
        }
      }
    ],
    "terminal_details": {
      "cf_terminal_id": 17269,
      "terminal_phone": "8971520311"
    }
  },
  "event_time": "2025-01-15T11:16:10+05:30",
  "type": "PAYMENT_SUCCESS_WEBHOOK"
}

async def setup_db_payment():
    db = get_database()
    order_id = payload["data"]["order"]["order_id"]
    existing = await db.payments.find_one({"id": order_id})
    if not existing:
        print(f"Order {order_id} not found in database. Creating an 'Active' record...")
        payment_data = {
            "id": order_id,
            "name": "Luxury Consultation",
            "amount": "₹2.00",
            "currency": "INR",
            "status": "Active",
            "merchant_name": "Luxury Merchant",
            "upi_id": "nexify@okicici",
            "created": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "creation_timestamp": datetime.now().timestamp(),
            "email": "test@gmail.com" # owner email
        }
        await db.payments.insert_one(payment_data)
        print(f"Created active payment with ID: {order_id}")
    else:
        print(f"Order {order_id} already exists in database with status: {existing.get('status')}")
        if existing.get("status") in ["Paid", "Success"]:
            print("Resetting status to 'Active' for test...")
            await db.payments.update_one({"id": order_id}, {"$set": {"status": "Active"}})

def send_webhook():
    url = "http://127.0.0.1:8000/webhook/cashfree"
    req = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode('utf-8'), 
        headers={'Content-Type': 'application/json'}
    )
    try:
        print("Sending Webhook POST request to /webhook/cashfree...")
        with urllib.request.urlopen(req) as response:
            print(f"Status Code: {response.getcode()}")
            print(f"Response: {response.read().decode('utf-8')}")
    except Exception as e:
        print(f"Webhook request failed: {e}")

async def verify_db_updated():
    db = get_database()
    order_id = payload["data"]["order"]["order_id"]
    updated = await db.payments.find_one({"id": order_id})
    if updated:
        print("\n--- Verified Payment Record ---")
        print(f"ID: {updated.get('id')}")
        print(f"Status: {updated.get('status')}")
        print(f"Amount: {updated.get('amount', '').replace('₹', 'Rs.')}")
        print(f"CF Payment ID: {updated.get('cf_payment_id')}")
        print(f"Payment Time: {updated.get('payment_time')}")
        print(f"Payment Method: {updated.get('payment_method')}")
    else:
        print(f"Error: Order {order_id} could not be verified in the database.")

async def main():
    await setup_db_payment()
    send_webhook()
    # Wait a bit for db write of webhook
    await asyncio.sleep(1)
    await verify_db_updated()

if __name__ == "__main__":
    asyncio.run(main())
