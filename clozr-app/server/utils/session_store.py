"""
Simple Session Store for OAuth nonces and tokens
In production, replace with a proper database (PostgreSQL, Redis, etc.)
"""

from typing import Optional, Dict
from datetime import datetime, timedelta
import json
import os

# In-memory storage (for development only)
# In production, use a database or Redis
_nonce_store: Dict[str, Dict] = {}
_token_store: Dict[str, str] = {}

# Nonce expiration time (5 minutes)
NONCE_EXPIRY = timedelta(minutes=5)


def store_nonce(shop: str, nonce: str) -> None:
    """
    Store nonce for OAuth state verification
    
    Args:
        shop: Shop domain
        nonce: Random nonce string
    """
    _nonce_store[shop] = {
        "nonce": nonce,
        "created_at": datetime.now(),
    }


def verify_nonce(shop: str, nonce: str) -> bool:
    """
    Verify nonce matches stored value and hasn't expired
    
    Args:
        shop: Shop domain
        nonce: Nonce to verify
    
    Returns:
        True if nonce is valid, False otherwise
    """
    if shop not in _nonce_store:
        return False
    
    stored = _nonce_store[shop]
    
    # Check expiration
    if datetime.now() - stored["created_at"] > NONCE_EXPIRY:
        del _nonce_store[shop]
        return False
    
    # Verify nonce matches
    if stored["nonce"] != nonce:
        return False
    
    # Clean up after verification
    del _nonce_store[shop]
    return True


def store_access_token(shop: str, access_token: str) -> None:
    """
    Store access token for a shop
    
    Args:
        shop: Shop domain
        access_token: Shopify access token
    """
    _token_store[shop] = access_token
    
    # In production, save to database:
    # db.save_token(shop, access_token)


def get_access_token(shop: str) -> Optional[str]:
    """
    Retrieve access token for a shop
    
    Args:
        shop: Shop domain
    
    Returns:
        Access token or None if not found
    """
    return _token_store.get(shop)

