import httpx
import asyncio

async def test_login():
    url = "http://127.0.0.1:8000/login"
    payloads = [
        {"email": "HKLLP", "password": "HKLLP123"},
        {"email": "merchant@payflow.com", "password": "password123"},
        {"email": "tech@global.com", "password": "password123"}
    ]
    
    async with httpx.AsyncClient() as client:
        for payload in payloads:
            try:
                res = await client.post(url, json=payload)
                print(f"Login for {payload['email']}: {res.status_code} - {res.json()}")
            except Exception as e:
                print(f"Error for {payload['email']}: {e}")

if __name__ == "__main__":
    asyncio.run(test_login())
