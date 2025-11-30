# server/routes/settings.py
from fastapi import APIRouter, Request, HTTPException
from server.session_store import get_token

import json
from pathlib import Path

router = APIRouter()

SETTINGS_FILE = Path(__file__).parent.parent / "merchant_settings.json"

# Load settings from file
def load_settings():
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r") as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}

# Save settings to file
def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

@router.get("/settings")
def get_settings(request: Request):
    shop = request.query_params.get("shop")
    if not shop:
        raise HTTPException(status_code=400, detail="Missing ?shop")
    settings = load_settings()
    return settings.get(shop, {})

@router.post("/settings")
async def update_settings(request: Request):
    shop = request.query_params.get("shop")
    if not shop:
        raise HTTPException(status_code=400, detail="Missing ?shop")

    # Ensure the shop is installed (token present)
    token = get_token(shop)
    if not token:
        raise HTTPException(status_code=403, detail="Shop not authenticated")

    # Read body
    new_settings = await request.json()

    settings = load_settings()
    settings[shop] = new_settings
    save_settings(settings)

    return {"status": "ok", "updated": new_settings}
