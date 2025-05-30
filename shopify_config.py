import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Shopify App Configuration
SHOPIFY_CONFIG = {
    "API_KEY": os.getenv("SHOPIFY_API_KEY"),
    "API_SECRET": os.getenv("SHOPIFY_API_SECRET"),
    "SCOPES": [
        "read_orders",
        "write_orders",
        "read_products",
        "read_customers",
        "read_shopify_payments_payouts",
        "read_shopify_payments_disputes"
    ],
    "HOST_NAME": os.getenv("BASE_URL", "http://localhost:8000"),
    "API_VERSION": "2024-01",
    "IS_EMBEDDED_APP": True,
    "APP_NAME": "Voice Call System"
}

# Installation URLs
INSTALL_URL = f"https://{SHOPIFY_CONFIG['HOST_NAME']}/api/shopify/connect"
REDIRECT_URL = f"https://{SHOPIFY_CONFIG['HOST_NAME']}/api/shopify/callback"

# Webhook Configuration
WEBHOOK_TOPICS = [
    "orders/create",
    "orders/updated",
    "orders/cancelled"
]

# Generate installation URL for a specific shop
def get_install_url(shop):
    return f"https://{shop}/admin/oauth/authorize?client_id={SHOPIFY_CONFIG['API_KEY']}&scope={','.join(SHOPIFY_CONFIG['SCOPES'])}&redirect_uri={REDIRECT_URL}" 