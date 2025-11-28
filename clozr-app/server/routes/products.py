# server/routes/products.py

import os
import requests
from fastapi import APIRouter, Request, HTTPException
from server.session_store import get_token

router = APIRouter()

API_VERSION = "2024-10"  # safe stable version

@router.get("/products")
def get_products(request: Request):
    shop = request.query_params.get("shop")

    if not shop:
        raise HTTPException(status_code=400, detail="Missing ?shop query parameter")

    # Load stored access token
    token = get_token(shop)
    if not token:
        raise HTTPException(status_code=403, detail="No access token for this shop. Please reinstall the app.")

    # Build Admin API URL
    url = f"https://{shop}/admin/api/{API_VERSION}/products.json"

    headers = {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"Shopify API request failed: {response.status_code} {response.text}"
        )

    return response.json()
