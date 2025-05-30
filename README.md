# Shopify Voice Call System Backend

This is the backend service for the Shopify Voice Call System, which automatically makes voice calls to customers in Urdu when new orders are placed.

## Features

- Shopify integration for new orders
- Automated voice calls in Urdu within 2 minutes of order placement
- Interactive voice response (IVR) system:
  - Press 1: Confirm order
  - Press 0: Cancel order
  - Press 2: Transfer to support team
- Order status management
- Manual call option for store owners
- MongoDB database for data persistence
- FastAPI backend with async support
- JWT authentication
- Webhook handling for Shopify events

## Prerequisites

- Python 3.8+
- MongoDB
- Twilio account
- Shopify Partner account

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following variables:
```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=shopify_voice

# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Twilio Configuration
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number
SUPPORT_PHONE_NUMBER=your-support-phone-number

# Application Configuration
BASE_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:5173

# Shopify Configuration
SHOPIFY_API_KEY=your-shopify-api-key
SHOPIFY_API_SECRET=your-shopify-api-secret
```

## Running the Application

1. Start MongoDB:
```bash
mongod
```

2. Run the FastAPI application:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- POST `/api/auth/register` - Register a new user
- POST `/api/auth/token` - Login and get access token
- GET `/api/auth/me` - Get current user information
- PUT `/api/auth/me` - Update user information

### Orders
- GET `/api/orders` - List all orders
- GET `/api/orders/{order_id}` - Get order details
- POST `/api/orders/{order_id}/call` - Initiate manual call
- PUT `/api/orders/{order_id}/status` - Update order status
- GET `/api/orders/{order_id}/call-status` - Get call status

### Shopify Integration
- POST `/api/shopify/connect` - Connect Shopify store
- GET `/api/shopify/webhook` - Handle Shopify webhooks
- GET `/api/shopify/store` - Get store information
- DELETE `/api/shopify/disconnect` - Disconnect store

### Voice Settings
- GET `/api/voice/settings` - Get voice settings
- PUT `/api/voice/settings` - Update voice settings
- POST `/api/voice/test` - Test voice call

## Development

### Project Structure
```
backend/
├── main.py              # FastAPI application
├── models.py            # Pydantic models
├── database.py          # MongoDB database utilities
├── auth.py             # Authentication utilities
├── voice_service.py    # Voice call service
├── shopify_service.py  # Shopify integration service
├── routers/            # API routers
│   ├── auth.py
│   ├── orders.py
│   ├── shopify.py
│   └── voice.py
├── requirements.txt    # Python dependencies
└── .env               # Environment variables
```

### Running Tests
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 