import os
import asyncio
import httpx
from datetime import datetime
from dotenv import load_dotenv

# Load .env
load_dotenv(dotenv_path="../.env")

async def test_payout_v1():
    app_id = os.getenv("CASHFREE_PAYOUT_APP_ID") or os.getenv("CASHFREE_APP_ID")
    secret_key = os.getenv("CASHFREE_PAYOUT_SECRET_KEY") or os.getenv("CASHFREE_SECRET_KEY")
    environment = os.getenv("CASHFREE_ENVIRONMENT", "sandbox")
    
    # Base URL for V1
    base_url = "https://payout-gamma.cashfree.com" if environment == "sandbox" else "https://payout-api.cashfree.com"
    auth_url = f"{base_url}/payout/v1/authorize"
    
    print(f"App ID: {app_id}")
    print(f"Secret Key: {secret_key[:10]}...")
    print(f"Environment: {environment}")
    print(f"Auth URL: {auth_url}")
    
    headers = {
        "X-Client-Id": app_id or "",
        "X-Client-Secret": secret_key or "",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Authorize
            res = await client.post(auth_url, headers=headers, timeout=10)
            print(f"Auth Status: {res.status_code}")
            print(f"Auth Response: {res.text}")
            
            if res.status_code == 200:
                data = res.json()
                if data.get("status") == "SUCCESS":
                    token = data["data"]["token"]
                    print("Token generated successfully.")
                    
                    # 2. Add Beneficiary (optional or test it)
                    add_bene_url = f"{base_url}/payout/v1.2/addBeneficiary"
                    bene_headers = {
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                    bene_payload = {
                        "beneId": "test_bene_123",
                        "name": "Test Beneficiary",
                        "email": "test@example.com",
                        "phone": "9999999999",
                        "bankAccount": "9999999999",
                        "ifsc": "UTIB0000001",
                        "address1": "Test Address",
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "pincode": "400001"
                    }
                    res_bene = await client.post(add_bene_url, json=bene_payload, headers=bene_headers, timeout=10)
                    print(f"Add Bene Status: {res_bene.status_code}")
                    print(f"Add Bene Response: {res_bene.text}")
                    
                    # 3. Request Transfer
                    transfer_url = f"{base_url}/payout/v1.2/requestTransfer"
                    transfer_payload = {
                        "beneId": "test_bene_123",
                        "amount": "10.00",
                        "transferId": f"WD-{int(datetime.now().timestamp())}",
                        "transferMode": "banktransfer",
                        "remarks": "Test Transfer"
                    }
                    res_tf = await client.post(transfer_url, json=transfer_payload, headers=bene_headers, timeout=10)
                    print(f"Transfer Status: {res_tf.status_code}")
                    print(f"Transfer Response: {res_tf.text}")
                    
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_payout_v1())
