# server/session_store.py
# Simple in-memory token store for dev only
SHOP_TOKENS = {}

def save_token(shop: str, token: str):
    SHOP_TOKENS[shop] = token

def get_token(shop: str):
    return SHOP_TOKENS.get(shop)

def delete_token(shop: str):
    SHOP_TOKENS.pop(shop, None)

def all_tokens():
    return SHOP_TOKENS.copy()
