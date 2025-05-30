from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Shopify Voice Call System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local development
        "https://*.myshopify.com",  # Shopify stores
        "https://admin.shopify.com",  # Shopify admin
        os.getenv("FRONTEND_URL", ""),  # Your frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    app.mongodb = app.mongodb_client[os.getenv("MONGODB_DB", "shopify_voice")]
    # Create indexes
    from database import Database
    db = Database(app.mongodb_client, os.getenv("MONGODB_DB", "shopify_voice"))
    await db.create_indexes()

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

# Import and include routers
from routers import orders, shopify, voice, auth

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(shopify.router, prefix="/api/shopify", tags=["Shopify"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 