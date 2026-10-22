import os
from pathlib import Path


class Settings:
    # --- Database ---
    DB_USER: str = "velos"
    DB_PASSWORD: str = "1234"
    DB_HOST: str = "0.0.0.0"
    DB_PORT: int = 3306
    DB_NAME: str = "velos"

    @property
    def DATABASE_URL(self) -> str:
        """
        Development-friendly database URL.
        If DB_HOST is left as the placeholder `0.0.0.0` we switch to a
        lightweight local SQLite DB so the app can run without a MySQL server.
        In production set DB_HOST/DB_USER/DB_PASSWORD appropriately.
        """
        # Allow explicit override via environment variable
        env = os.getenv('VEL0S_DATABASE_URL')
        if env:
            return env

        if self.DB_HOST == "0.0.0.0":
            # Use a local sqlite file inside the project for easy local dev
            db_file = Path(__file__).parents[2] / 'velos_dev.sqlite'
            return f"sqlite:///{db_file}"

        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # --- JWT ---
    SECRET_KEY: str = "f5f6cfcb44c92deaffbeae47dca73bb6b209f35ad226df224af0c235a33090c6"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- App ---
    APP_NAME: str = "Mini Banking System API"
    APP_VERSION: str = "1.0.0"


settings = Settings()
