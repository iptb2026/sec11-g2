import os


class Settings:
    # --- Database ---
    DB_USER: str = os.getenv("DB_USER", "salva")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "salva12")
    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_NAME: str = os.getenv("DB_NAME", "salva")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # --- JWT ---
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "f5f6cfcb44c92deaffbeae47dca73bb6b209f35ad226df224af0c235a33090c6"
    )
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # --- App ---
    APP_NAME: str = os.getenv("APP_NAME", "Salva Banking System API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")


settings = Settings()