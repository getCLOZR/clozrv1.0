# server/shopify_oauth.py
import os
import hmac
import hashlib
import urllib.parse
import requests
from fastapi import HTTPException

API_KEY = os.getenv("SHOPIFY_API_KEY")
API_SECRET = os.getenv("SHOPIFY_API_SECRET")
SCOPES = os.getenv("SCOPES", "read_products,write_products")
HOST = os.getenv("HOST")  # e.g. https://your-ngrok-url.ngrok-free.dev

if not (API_KEY and API_SECRET and HOST):
    raise RuntimeError("Missing SHOPIFY_API_KEY, SHOPIFY_API_SECRET or HOST env var")

def build_install_redirect(shop: str):
    """
    Build URL to redirect merchant to Shopify OAuth consent screen.
    """
    if not shop:
        raise HTTPException(status_code=400, detail="Missing shop")
    redirect_uri = urllib.parse.urljoin(HOST, "/auth/callback")
    # construct oauth url
    install_url = (
        f"https://{shop}/admin/oauth/authorize"
        f"?client_id={API_KEY}"
        f"&scope={urllib.parse.quote(SCOPES)}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
    )
    return {"redirect": install_url}

def verify_hmac(params: dict) -> bool:
    """
    Verify Shopify HMAC. `params` should be a dict of query params.
    Returns True if HMAC valid.
    """
    params = params.copy()
    hmac_sent = params.pop("hmac", None)
    if not hmac_sent:
        return False

    # Shopify docs: sort lexicographically and join key=value with & (exclude hmac)
    # Ensure values are the raw query string values (already percent-decoded by FastAPI).
    sorted_params = sorted((k, v) for k, v in params.items() if k != "signature")
    message = "&".join([f"{k}={v}" for k, v in sorted_params])

    computed = hmac.new(API_SECRET.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, hmac_sent)

def exchange_code_for_token(shop: str, code: str) -> dict:
    """
    Exchange temporary code for permanent access token.
    """
    token_url = f"https://{shop}/admin/oauth/access_token"
    payload = {
        "client_id": API_KEY,
        "client_secret": API_SECRET,
        "code": code
    }
    resp = requests.post(token_url, json=payload, timeout=10)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Token exchange failed: {resp.status_code} {resp.text}")
    return resp.json()  # expected to contain 'access_token'
