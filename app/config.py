from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # AI Provider Selection ("gemini" or "claude")
    AI_PROVIDER: str = "gemini"

    # Google Gemini API Configuration (Server-Side ONLY)
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Claude API Configuration (Compatibility fallback, Server-Side ONLY)
    ANTHROPIC_API_KEY: Optional[str] = None
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"

    # Firebase / Firestore Configuration (Single Source of Truth)
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    FIRESTORE_DATABASE_ID: str = "(default)"
    USE_FIREBASE_EMULATOR: bool = False
    FIRESTORE_EMULATOR_HOST: Optional[str] = None

    # Database Configuration (PostgreSQL with RLS / Multi-tenant metadata)
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
