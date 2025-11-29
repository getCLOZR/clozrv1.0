# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "CLOZR Product Intelligence Engine"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://user:password@localhost:5432/clozr")

    # Shopify
    SHOPIFY_STORE_DOMAIN: str | None = os.getenv("SHOPIFY_STORE_DOMAIN")
    SHOPIFY_ADMIN_ACCESS_TOKEN: str | None = os.getenv("SHOPIFY_ADMIN_ACCESS_TOKEN")

settings = Settings()
