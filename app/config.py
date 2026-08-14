from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Claude API Configuration (Server-Side ONLY)
    ANTHROPIC_API_KEY: Optional[str] = None
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"

    # Database Configuration (PostgreSQL with RLS)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/whatsapp_sales_db"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/whatsapp_sales_db"

    # WhatsApp Business Cloud API Configuration
    WHATSAPP_VERIFY_TOKEN: str = "default_verify_token_replace_me"
    WHATSAPP_APP_SECRET: str = "default_app_secret_replace_me"
    WHATSAPP_API_VERSION: str = "v20.0"
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v20.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
