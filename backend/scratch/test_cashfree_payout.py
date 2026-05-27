import os
import asyncio
import httpx
from datetime import datetime
from dotenv import load_dotenv

# Load .env
load_dotenv(dotenv_path="../.env")

async def test_payout():
    app_id = os.getenv("CASHFREE_PAYOUT_APP_ID") or os.getenv("CASHFREE_APP_ID")
    secret_key = os.getenv("CASHFREE_PAYOUT_SECRET_KEY") or os.getenv("CASHFREE_SECRET_KEY")
    environment = os.getenv("CASHFREE_ENVIRONMENT", "sandbox")
    
    base_url = "https://sandbox.cashfree.com" if environment == "sandbox" else "https://api.cashfree.com"
    transfer_url = f"{base_url}/payout/transfers"
    
    print(f"App ID: {app_id}")
    print(f"Secret Key: {secret_key[:10]}...")
    print(f"Environment: {environment}")
    print(f"URL: {transfer_url}")
    
    headers = {
        "x-client-id": app_id or "",
        "x-client-secret": secret_key or "",
        "x-api-version": "2024-01-01",
        "Content-Type": "application/json"
    }
    
    payload = {
        "transfer_id": f"TEST-WD-{int(datetime.now().timestamp())}",
        "transfer_amount": 10.0,
        "transfer_currency": "INR",
        "transfer_mode": "imps",
        "beneficiary_details": {
            "beneficiary_name": "Test Merchant Payout",
            "beneficiary_instrument_details": {
                "bank_account_number": "9999999999",
                "bank_ifsc": "UTIB0000001"
            },
            "beneficiary_contact_details": {
                "beneficiary_email": "test@example.com",
                "beneficiary_phone": "9999999999"
            }
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(transfer_url, json=payload, headers=headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_payout())
