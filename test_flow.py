import requests
import json
import time

# API endpoints
BASE_URL = "http://localhost:8000/api"
AUTH_URL = f"{BASE_URL}/auth"
ORDERS_URL = f"{BASE_URL}/orders"

def test_flow():
    try:
        # 1. Register a new user
        print("\n1. Registering new user...")
        register_data = {
            "email": "test@example.com",
            "hashed_password": "testpassword123",  # Changed to match our User model
            "is_active": True
        }
        register_response = requests.post(f"{AUTH_URL}/register", json=register_data)
        if register_response.status_code != 200:
            print("Registration failed:", register_response.text)
            return
        print("Register Response:", register_response.json())

        # 2. Login to get token
        print("\n2. Logging in...")
        login_data = {
            "username": "test@example.com",
            "password": "testpassword123"
        }
        login_response = requests.post(f"{AUTH_URL}/token", data=login_data)
        if login_response.status_code != 200:
            print("Login failed:", login_response.text)
            return
        token = login_response.json()["access_token"]
        print("Login successful!")

        # 3. Create test orders
        print("\n3. Creating test orders...")
        headers = {"Authorization": f"Bearer {token}"}
        
        test_orders = [
            {
                "shopifyOrderId": "TEST-001",
                "orderNumber": "TEST-001",
                "customerName": "Test Customer 1",
                "customerPhone": "+1234567890",
                "amount": 99.99,
                "status": "pending",
                "callStatus": "not_called"
            },
            {
                "shopifyOrderId": "TEST-002",
                "orderNumber": "TEST-002",
                "customerName": "Test Customer 2",
                "customerPhone": "+1987654321",
                "amount": 149.99,
                "status": "pending",
                "callStatus": "not_called"
            }
        ]

        for order in test_orders:
            order_response = requests.post(
                ORDERS_URL,
                json=order,
                headers=headers
            )
            if order_response.status_code != 200:
                print(f"Failed to create order {order['orderNumber']}:", order_response.text)
                continue
            print(f"Created order {order['orderNumber']}:", order_response.json())

        # 4. Get all orders
        print("\n4. Getting all orders...")
        orders_response = requests.get(ORDERS_URL, headers=headers)
        if orders_response.status_code != 200:
            print("Failed to get orders:", orders_response.text)
            return
        print("Orders:", orders_response.json())

        # 5. Test manual call for first order
        print("\n5. Testing manual call...")
        orders = orders_response.json()
        if not orders:
            print("No orders found to test call")
            return
            
        first_order = orders[0]
        call_response = requests.post(
            f"{ORDERS_URL}/{first_order['id']}/call",
            headers=headers
        )
        if call_response.status_code != 200:
            print("Failed to initiate call:", call_response.text)
            return
        print("Call initiated:", call_response.json())

        # 6. Check call status
        print("\n6. Checking call status...")
        time.sleep(2)  # Wait a bit for the call to process
        status_response = requests.get(
            f"{ORDERS_URL}/{first_order['id']}/call-status",
            headers=headers
        )
        if status_response.status_code != 200:
            print("Failed to get call status:", status_response.text)
            return
        print("Call status:", status_response.json())

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the backend is running at http://localhost:8000")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    test_flow() 