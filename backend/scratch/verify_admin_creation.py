import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def api_call(url, method="GET", data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

# 1. Log in as system admin
print("Logging in as default system admin...")
status, res = api_call(f"{BASE_URL}/login/admin", "POST", {
    "email": "admin@payflow.com",
    "password": "password123"
})
if status != 200:
    print(f"FAILED: Could not login as default admin. Status: {status}, Response: {res}")
    sys.exit(1)

admin_token = res.get("session_token")
print(f"Success! Admin Token: {admin_token}\n")

# 2. Create a custom admin account
admin_email = "test_custom_admin@payflow.com"
admin_password = "SecureAdminPassword123"
print(f"Creating a new admin account: {admin_email}...")
status, res = api_call(f"{BASE_URL}/admin/create-merchant", "POST", {
    "name": "Test Custom Admin",
    "email": admin_email,
    "password": admin_password,
    "role": "admin"
}, token=admin_token)

if status != 200:
    print(f"FAILED: Could not create admin account. Status: {status}, Response: {res}")
    sys.exit(1)

print("Create response:", res)
if res.get("status") != "success":
    print("FAILED: Creation was not successful")
    sys.exit(1)
print("Success!\n")

# 3. Verify portal isolation: attempt to login as merchant
print("Verifying portal isolation: attempting to login as merchant...")
status, res = api_call(f"{BASE_URL}/login/merchant", "POST", {
    "email": admin_email,
    "password": admin_password
})
print("Merchant Login response (status code:", status, "):", res)
if res.get("status") == "success":
    print("FAILED: Custom admin was able to log in to the Merchant portal! Portal isolation is broken.")
    sys.exit(1)
else:
    print("Isolation success: Custom admin login to Merchant portal rejected.\n")

# 4. Verify admin login
print("Attempting to login via Admin portal...")
status, res = api_call(f"{BASE_URL}/login/admin", "POST", {
    "email": admin_email,
    "password": admin_password
})
print("Admin Login response (status code:", status, "):", res)
if res.get("status") != "success":
    print("FAILED: Custom admin could not log in to the Admin portal.")
    sys.exit(1)
print("Success! Custom admin logged in successfully.\n")

# 5. Verify exclusion from merchant directory
print("Verifying that the custom admin does not show up in the merchants list...")
status, res = api_call(f"{BASE_URL}/admin/merchants", "GET", token=admin_token)
if status != 200:
    print(f"FAILED: Could not retrieve merchants. Status: {status}")
    sys.exit(1)

found_admin = False
for merchant in res:
    if merchant.get("email") == admin_email:
        found_admin = True
        break

if found_admin:
    print("FAILED: Custom admin was found in the merchants list!")
    sys.exit(1)
else:
    print("Success: Custom admin is excluded from the merchants directory.\n")

# Cleanup: Delete the custom admin user from the database
print("Cleaning up: Deleting custom admin user...")
status, res = api_call(f"{BASE_URL}/admin/merchants/{admin_email}", "DELETE", token=admin_token)
print("Delete response:", res)

print("\nALL TESTS PASSED SUCCESSFULLY! BOTH VISUAL EXCLUSIONS AND FUNCTIONAL ROLE ISOLATION ARE VERIFIED.")
