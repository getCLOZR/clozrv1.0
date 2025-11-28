from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import RedirectResponse
from server.shopify_oauth import build_install_redirect

router = APIRouter()

@router.get("/install")
def install(shop: str = Query(None)):
    if not shop:
        raise HTTPException(status_code=400, detail="Missing shop")

    # Get Shopify OAuth redirect URL
    install_data = build_install_redirect(shop)
    oauth_url = install_data["redirect"]

    # ⭐ Return a real redirect
    return RedirectResponse(url=oauth_url)
