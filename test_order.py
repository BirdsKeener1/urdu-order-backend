import requests
import json

# API endpoint
API_URL = "http://localhost:8000/api/orders"

# Test order data
test_order = {
    "shopifyOrderId": "TEST-001",
    "orderNumber": "TEST-001",
    "customerName": "Test Customer",
    "customerPhone": "+1234567890",
    "amount": 99.99,
    "status": "pending",
    "callStatus": "not_called"
}

try:
    # Create the order
    response = requests.post(
        API_URL,
        json=test_order,
        headers={"Content-Type": "application/json"}
    )

    # Print the response
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        print("Order created successfully:", response.json())
    else:
        print("Failed to create order:", response.text)

except requests.exceptions.ConnectionError:
    print("Error: Could not connect to the server. Make sure the backend is running at http://localhost:8000")
except Exception as e:
    print(f"An error occurred: {str(e)}") 