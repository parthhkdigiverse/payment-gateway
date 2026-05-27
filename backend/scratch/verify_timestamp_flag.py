import sys
import os

# Adjust path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from schemas import Payment, Settlement, Customer, ContactInquiry, MerchantProfile, SupportTicket, MerchantInvite, CreateMerchantRequest

def test_schemas():
    print("Verifying schemas validate correctly with timestamp: bool = True...")
    
    # 1. Payment
    payment = Payment(name="Test User", amount="100.00")
    assert payment.timestamp is True
    print("[OK] Payment schema matches timestamp=True")
    
    # 2. CreateMerchantRequest
    req = CreateMerchantRequest(name="New Merchant", email="test@merchant.com", password="password")
    assert req.timestamp is True
    print("[OK] CreateMerchantRequest schema matches timestamp=True")

if __name__ == "__main__":
    test_schemas()
    print("All checks passed successfully!")
