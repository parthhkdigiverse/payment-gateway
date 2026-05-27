import urllib.request
import urllib.parse
import json

def test_auth():
    base_url = "http://127.0.0.1:8000"
    
    # 1. Login
    login_data = {
        "email": "merchant@payflow.com",
        "password": "password123",
        "required_role": "merchant"
    }
    
    print(f"Attempting login to {base_url}/login/merchant...")
    req = urllib.request.Request(
        f"{base_url}/login/merchant",
        data=json.dumps(login_data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as res:
            res_body = res.read().decode("utf-8")
            print(f"Login Response status: {res.status}")
            print(f"Login Response body: {res_body}")
            data = json.loads(res_body)
    except Exception as e:
        if hasattr(e, 'read'):
            print(f"Login request failed: {e} - {e.read().decode('utf-8')}")
        else:
            print(f"Login request failed: {e}")
        return
        
    token = data.get("session_token")
    print(f"Obtained token: {token}")
    
    # 2. Get payments
    print(f"\nFetching payments from {base_url}/merchant/payments...")
    req_payments = urllib.request.Request(
        f"{base_url}/merchant/payments",
        headers={"Authorization": f"Bearer {token}"},
        method="GET"
    )
    
    try:
        with urllib.request.urlopen(req_payments) as res_payments:
            print(f"Payments Response status: {res_payments.status}")
            print(f"Payments Response body: {res_payments.read().decode('utf-8')}")
    except Exception as e:
        if hasattr(e, 'read'):
            print(f"Payments request failed: {e} - {e.read().decode('utf-8')}")
        else:
            print(f"Payments request failed: {e}")

if __name__ == "__main__":
    test_auth()
