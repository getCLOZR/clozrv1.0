# # app/shopify_client.py
# from typing import List, Dict, Any
# import requests
# from app.config import settings

# SHOPIFY_STORE_DOMAIN = settings.SHOPIFY_STORE_DOMAIN
# SHOPIFY_ADMIN_ACCESS_TOKEN = settings.SHOPIFY_ADMIN_ACCESS_TOKEN
# API_VERSION = "2024-01"

# class ShopifyClientError(Exception):
#     pass

# def get_products(limit: int = 50) -> List[Dict[str, Any]]:
#     if not SHOPIFY_STORE_DOMAIN or not SHOPIFY_ADMIN_ACCESS_TOKEN:
#         raise ShopifyClientError("Missing SHOPIFY_STORE_DOMAIN or SHOPIFY_ADMIN_ACCESS_TOKEN")

#     url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/{API_VERSION}/products.json"
#     headers = {
#         "X-Shopify-Access-Token": SHOPIFY_ADMIN_ACCESS_TOKEN,
#     }
#     params = {"limit": limit}

#     print("DEBUG URL:", url)
#     print("DEBUG TOKEN PREFIX:", SHOPIFY_ADMIN_ACCESS_TOKEN[:8])

#     resp = requests.get(url, headers=headers, params=params, timeout=30)

#     if resp.status_code != 200:
#         raise ShopifyClientError(f"Shopify API error {resp.status_code}: {resp.text}")

#     data = resp.json()
#     return data.get("products", [])




