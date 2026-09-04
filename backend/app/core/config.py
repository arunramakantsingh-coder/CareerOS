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
        "http://localhost:8000",
    ]

    AUTH_SECRET_KEY: str = "your-secret-key-change-this-in-production"
    AUTH_ALGORITHM: str = "HS256"
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    FRONTEND_BASE_URL: str = "http://localhost:3000"

    # Centralized bootstrap allow-list for local development. Production should use role=developer/admin.
    DEVELOPER_EMAILS: List[str] = []

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
