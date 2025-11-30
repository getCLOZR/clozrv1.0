# server/main.py
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from server.routes import install, auth_callback, products, settings
from pathlib import Path

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
app.include_router(products.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
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
    frontend_path = Path(__file__).parent.parent / "frontend" / "dist" / "index.html"
    if frontend_path.exists():
        return FileResponse(str(frontend_path))
    else:
        # Fallback if frontend not built yet
        return HTMLResponse("""
        <h1>CLOZR App</h1>
        <p>Frontend not built. Run: cd frontend && npm run build</p>
        <p>Or access the app via the embedded Shopify admin.</p>
        """)

@app.get("/health")
def health():
    return {"status": "ok"}

# Optional debug route to show saved tokens (dev-only)
@app.get("/debug/tokens")
def debug_tokens():
    from server.session_store import all_tokens
    return all_tokens()


# Mount static files if directory exists
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    # Mount assets directory so /assets/... paths work
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
    # Mount vite.svg if it exists
    vite_svg = frontend_dist / "vite.svg"
    if vite_svg.exists():
        @app.get("/vite.svg")
        async def vite_svg_file():
            return FileResponse(str(vite_svg))
