from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from typing import Dict, Any
from models import User, Store
from database import Database
from shopify_service import ShopifyService
from auth import get_current_active_user
import os

router = APIRouter()
db = Database()

# Required Shopify scopes
SHOPIFY_SCOPES = [
    "read_orders",
    "write_orders",
    "read_products",
    "read_customers",
    "read_shopify_payments_payouts",
    "read_shopify_payments_disputes"
]

@router.get("/auth")
async def shopify_auth(shop: str):
    """Generate Shopify OAuth URL"""
    redirect_uri = f"{os.getenv('BACKEND_URL')}/api/shopify/callback"
    auth_url = ShopifyService.generate_auth_url(shop, SHOPIFY_SCOPES, redirect_uri)
    return {"auth_url": auth_url}

@router.get("/callback")
async def shopify_callback(
    shop: str,
    code: str,
    state: str,
    db: Database = Depends()
):
    """Handle Shopify OAuth callback"""
    try:
        # Exchange code for access token
        token_data = await ShopifyService.get_access_token(shop, code)
        
        # Initialize Shopify service
        shopify_service = ShopifyService(shop, token_data["access_token"])
        
        # Get shop info
        shop_info = shopify_service.get_shop_info()
        
        # Create webhook for new orders
        webhook_url = f"{os.getenv('BACKEND_URL')}/api/shopify/webhook"
        webhook = shopify_service.create_webhook("orders/create", webhook_url)
        
        # Save store information
        store = Store(
            shop_id=shop_info["id"],
            shop_name=shop_info["name"],
            shop_domain=shop_info["domain"],
            access_token=token_data["access_token"],
            webhook_id=webhook["id"]
        )
        await db.create_store(store)
        
        # Redirect to frontend
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        return RedirectResponse(f"{frontend_url}/dashboard?shop={shop}")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect store: {str(e)}"
        )

@router.post("/webhook")
async def shopify_webhook(request: Request):
    """Handle Shopify webhooks"""
    # Get HMAC header
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256")
    if not hmac_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing HMAC header"
        )
    
    # Get request body
    body = await request.body()
    
    # Verify webhook
    if not ShopifyService.verify_webhook(body, hmac_header):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    
    # Parse webhook data
    data = await request.json()
    
    # Handle new order
    if request.headers.get("X-Shopify-Topic") == "orders/create":
        # Get store from shop domain
        shop_domain = request.headers.get("X-Shopify-Shop-Domain")
        store = await db.get_store_by_domain(shop_domain)
        
        if store:
            # Initialize Shopify service
            shopify_service = ShopifyService(shop_domain, store.access_token)
            
            # Get order details
            order = shopify_service.get_order(data["id"])
            
            if order:
                # Save order to database
                await db.create_order(order)
                
                # Initiate call
                from voice_service import VoiceService
                voice_service = VoiceService()
                call = voice_service.make_call(order["phone"], order["name"])
                
                if call:
                    # Update order with call information
                    await db.update_order_call_status(order["id"], call["sid"], "initiated")
    
    return {"status": "success"}

@router.get("/store")
async def get_store_info(
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends()
):
    """Get connected store information"""
    store = await db.get_store_by_user_id(current_user.id)
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No store connected"
        )
    
    # Initialize Shopify service
    shopify_service = ShopifyService(store.shop_domain, store.access_token)
    
    # Get shop info
    shop_info = shopify_service.get_shop_info()
    
    return {
        "store": store.dict(),
        "shop_info": shop_info
    }

@router.delete("/disconnect")
async def disconnect_store(
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends()
):
    """Disconnect Shopify store"""
    store = await db.get_store_by_user_id(current_user.id)
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No store connected"
        )
    
    try:
        # Initialize Shopify service
        shopify_service = ShopifyService(store.shop_domain, store.access_token)
        
        # Delete webhook
        if store.webhook_id:
            shopify_service.delete_webhook(store.webhook_id)
        
        # Delete store from database
        await db.delete_store(store.id)
        
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to disconnect store: {str(e)}"
        ) 