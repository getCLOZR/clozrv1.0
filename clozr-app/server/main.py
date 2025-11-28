# server/main.py
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse, Response
from server.routes import install, auth_callback, products
import os

app = FastAPI()

# middleware to skip ngrok warning page
@app.middleware("http")
async def add_ngrok_header(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

# include routers
app.include_router(install.router)
app.include_router(auth_callback.router)
app.include_router(products.router)

@app.get("/")
def index(request: Request):
    shop = request.query_params.get("shop")

    if not shop:
        return HTMLResponse("<h3>Missing ?shop parameter</h3>", status_code=400)

    from server.session_store import get_token
    token = get_token(shop)

    # If no token → force OAuth
    if not token:
        # Redirect to /install
        return RedirectResponse(url=f"/install?shop={shop}")

    # If token exists → load app normally
    return HTMLResponse("<h1>CLOZR App (authenticated)</h1>")

@app.get("/health")
def health():
    return {"status": "ok"}

# Optional debug route to show saved tokens (dev-only)
@app.get("/debug/tokens")
def debug_tokens():
    from server.session_store import all_tokens
    return all_tokens()
