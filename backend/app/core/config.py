from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    APP_NAME: str = "CareerOS"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3100",
        "http://localhost:8000",
    ]

    # Authentication / JWT foundation. Override through environment variables.
    AUTH_SECRET_KEY: str = "development-only-change-me"
    AUTH_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

