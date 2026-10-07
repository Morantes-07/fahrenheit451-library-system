import os
from pathlib import Path

from dotenv import load_dotenv

# .env lives in src/ (one level above utils/)
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def _bool(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes", "on")


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Library API")
    DEBUG: bool = _bool(os.getenv("DEBUG", "false"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./library.db")
    CORS_ORIGINS: list[str] = [
        o.strip()
        for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
        if o.strip()
    ]
    LOAN_DAYS: int = int(os.getenv("LOAN_DAYS", "14"))
    MAX_ACTIVE_LOANS: int = int(os.getenv("MAX_ACTIVE_LOANS", "5"))
    FINE_PER_DAY: float = float(os.getenv("FINE_PER_DAY", "0.50"))


settings = Settings()
