import shopify
import hmac
import hashlib
import base64
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode
import os

class ShopifyService:
    def __init__(self, shop_url: str, access_token: str):
        self.shop_url = shop_url
        self.access_token = access_token
        self.api_version = os.getenv("SHOPIFY_API_VERSION", "2024-01")
        
        # Initialize Shopify session
        shopify.Session.setup(
            api_key=os.getenv("SHOPIFY_API_KEY"),
            secret=os.getenv("SHOPIFY_API_SECRET")
        )
        
        # Activate session
        session = shopify.Session(shop_url, self.api_version, access_token)
        shopify.ShopifyResource.activate_session(session)

    @staticmethod
    def verify_webhook(data: bytes, hmac_header: str) -> bool:
        """Verify Shopify webhook signature"""
        calculated_hmac = base64.b64encode(
            hmac.new(
                os.getenv("SHOPIFY_API_SECRET").encode('utf-8'),
                data,
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        return hmac.compare_digest(calculated_hmac, hmac_header)

    @staticmethod
    def generate_auth_url(shop: str, scopes: List[str], redirect_uri: str) -> str:
        """Generate Shopify OAuth URL"""
        api_key = os.getenv("SHOPIFY_API_KEY")
        scopes_str = ",".join(scopes)
        
        # Generate state parameter for security
        state = base64.b64encode(os.urandom(16)).decode('utf-8')
        
        params = {
            "client_id": api_key,
            "scope": scopes_str,
            "redirect_uri": redirect_uri,
            "state": state,
            "grant_options[]": "per-user"
        }
        
        return f"https://{shop}/admin/oauth/authorize?{urlencode(params)}"

    @staticmethod
    async def get_access_token(shop: str, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        api_key = os.getenv("SHOPIFY_API_KEY")
        api_secret = os.getenv("SHOPIFY_API_SECRET")
        
        # Make request to Shopify
        session = shopify.Session(shop, os.getenv("SHOPIFY_API_VERSION", "2024-01"))
        token = session.request_token({
            "client_id": api_key,
            "client_secret": api_secret,
            "code": code
        })
        
        return {
            "access_token": token,
            "shop": shop
        }

    def get_shop_info(self) -> Dict[str, Any]:
        """Get shop information"""
        shop = shopify.Shop.current()
        return {
            "id": shop.id,
            "name": shop.name,
            "email": shop.email,
            "domain": shop.domain,
            "plan_name": shop.plan_name,
            "myshopify_domain": shop.myshopify_domain
        }

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order details"""
        try:
            order = shopify.Order.find(order_id)
            return {
                "id": order.id,
                "name": order.name,
                "email": order.email,
                "phone": order.phone,
                "total_price": order.total_price,
                "currency": order.currency,
                "financial_status": order.financial_status,
                "fulfillment_status": order.fulfillment_status,
                "created_at": order.created_at,
                "updated_at": order.updated_at
            }
        except Exception as e:
            print(f"Error getting order: {str(e)}")
            return None

    def create_webhook(self, topic: str, address: str) -> Dict[str, Any]:
        """Create webhook"""
        webhook = shopify.Webhook()
        webhook.topic = topic
        webhook.address = address
        webhook.format = "json"
        webhook.save()
        
        return {
            "id": webhook.id,
            "topic": webhook.topic,
            "address": webhook.address,
            "format": webhook.format
        }

    def delete_webhook(self, webhook_id: str) -> bool:
        """Delete webhook"""
        try:
            webhook = shopify.Webhook.find(webhook_id)
            webhook.destroy()
            return True
        except Exception as e:
            print(f"Error deleting webhook: {str(e)}")
            return False

    def get_webhooks(self) -> List[Dict[str, Any]]:
        """Get all webhooks"""
        webhooks = shopify.Webhook.find()
        return [{
            "id": webhook.id,
            "topic": webhook.topic,
            "address": webhook.address,
            "format": webhook.format
        } for webhook in webhooks]

    def update_order_status(self, order_id: str, financial_status: str) -> bool:
        """Update order status"""
        try:
            order = shopify.Order.find(order_id)
            order.financial_status = financial_status
            order.save()
            return True
        except Exception as e:
            print(f"Error updating order status: {str(e)}")
            return False 