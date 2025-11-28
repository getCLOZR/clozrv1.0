# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "CLOZR Product Intelligence Engine"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://user:password@localhost:5432/clozr")

settings = Settings()
