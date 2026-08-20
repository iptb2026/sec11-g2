class Settings:
    # --- Database ---
    DB_USER: str = "costas"
    DB_PASSWORD: str = "1234"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_NAME: str = "db"

    @property
    def DATABASE_URL(self):
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # --- JWT ---
    SECRET_KEY: str = "..."
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- App ---
    APP_NAME: str = "Mini Banking System API"
    APP_VERSION: str = "1.0.0"


settings = Settings()
