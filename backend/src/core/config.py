from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Multi-Tenant User API"
    API_V1_STR: str = "/api/v1"

    # Security
    GATEWAY_PSK: str = "default-dev-secret"

    # Supabase (for service role actions)
    SUPABASE_URL: str = "http://localhost:8000"
    SUPABASE_KEY: str = "placeholder_key"  # Service Role Key

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

    # Feature Flags
    UNLEASH_URL: Optional[str] = None
    UNLEASH_APP_NAME: str = "user-management-api"
    UNLEASH_API_TOKEN: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


settings = Settings()
