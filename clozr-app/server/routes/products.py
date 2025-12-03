# server/routes/products.py

import os
import json
import requests
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException, Query
from server.session_store import get_token

router = APIRouter()

API_VERSION = "2024-10"  # safe stable version

# Directory to store exported product JSON files
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def save_products_to_json(shop: str, products_data: dict):
    """
    Save products data to a JSON file for local import into clozr-engine.
    File format matches what clozr-engine expects: {"products": [...]}
    """
    # Sanitize shop domain for filename (replace dots and special chars)
    safe_shop_name = shop.replace(".", "_").replace("-", "_")
    filename = f"products_{safe_shop_name}.json"
    filepath = DATA_DIR / filename

    # Ensure the data is in the correct format
    export_data = {
        "products": products_data.get("products", []),
        "shop": shop,
        "exported_at": products_data.get("exported_at")  # Will be added if not present
    }

    # Add timestamp if not present
    if "exported_at" not in export_data:
        from datetime import datetime
        export_data["exported_at"] = datetime.now().isoformat()

    # Write to file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    return filepath


@router.get("/products")
def get_products(
    request: Request,
    mode: str = Query("summary", description="summary (default) or full"),
):
    """
    Fetch products for a shop.
    - mode=summary (default): returns just a count (used by frontend)
    - mode=full: returns the full Shopify products JSON
    
    Products are automatically saved to a JSON file in server/data/ for local import into clozr-engine.
    """
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
            detail=f"Shopify API request failed: {response.status_code} {response.text}",
        )

    products_data = response.json()

    # Save products to JSON file for clozr-engine import
    try:
        filepath = save_products_to_json(shop, products_data)
        print(f"✅ Saved {len(products_data.get('products', []))} products to {filepath}")
    except Exception as e:
        print(f"⚠️  Warning: Failed to save products to JSON file: {e}")
        # Don't fail the request if file save fails

    # Full JSON for export/sharing
    if mode == "full":
        return products_data

    # Default: just a count (for dashboard)
    products_list = products_data.get("products", [])
    return {"count": len(products_list)}
