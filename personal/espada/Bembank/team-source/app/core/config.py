import os
import secrets
from pathlib import Path


class Settings:
    # --- Database ---
    DB_USER: str = "evanoso"
    DB_PASSWORD: str = "1234"
    DB_HOST: str = "0.0.0.0"
    DB_PORT: int = 3306
    DB_NAME: str = "evanoso"

    @property
    def DATABASE_URL(self) -> str:
        # shortcut: SQLite is for a local classroom demo, use MySQL for concurrent deployment.
        return os.environ.get('BEMBANK_DATABASE_URL', f"sqlite:///{Path(__file__).resolve().parents[2] / 'bembank-demo.sqlite3'}")

    # --- JWT ---
    SECRET_KEY: str = os.environ.get('BEMBANK_SECRET_KEY') or secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- App ---
    APP_NAME: str = "Mini Banking System API"
    APP_VERSION: str = "1.0.0"


settings = Settings()
