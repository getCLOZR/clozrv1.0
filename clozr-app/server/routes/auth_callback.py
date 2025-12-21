# server/routes/auth_callback.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from server.shopify_oauth import verify_hmac, exchange_code_for_token
from server.session_store import save_token

router = APIRouter()

@router.get("/auth/callback")
async def auth_callback(request: Request):
    # Build a plain dict from query params
    params = dict(request.query_params)
    shop = params.get("shop")
    code = params.get("code")

    # verify HMAC
    if not verify_hmac(params):
        raise HTTPException(status_code=400, detail="HMAC verification failed")

    # exchange code for token
    token_response = exchange_code_for_token(shop, code)
    access_token = token_response.get("access_token")
    if not access_token:
        raise HTTPException(status_code=500, detail="No access token returned")

    # save token (dev only; persist in db in prod)
    save_token(shop, access_token)
    print(f"✅ Token saved for shop: {shop}")

    # Return a friendly HTML page (Shopify will then load embedded app root)
    body = f"""
    <html>
      <body>
        <h2>CLOZR installed for {shop}</h2>
        <p>Installation successful. You can close this page and continue in the Shopify admin.</p>
        <script>
          // If loaded outside the admin, redirect to root
          window.location = "/?shop={shop}";
        </script>
      </body>
    </html>
    """
    return HTMLResponse(body)
