import httpx, asyncio, os

async def main():
    r = await httpx.AsyncClient().post('https://sandbox.cashfree.com/pg/orders', headers={
        'x-client-id': os.environ['CF_CLIENT_ID'],
        'x-client-secret': os.environ['CF_CLIENT_SECRET'],
        'x-api-version': '2023-08-01',
        'Content-Type': 'application/json'
    }, json={
        'order_id': 'test_9999',
        'order_amount': 10,
        'order_currency': 'INR',
        'customer_details': {
            'customer_id': '123',
            'customer_phone': '9999999999'
        }
    })
    print(r.status_code, r.text)

asyncio.run(main())
