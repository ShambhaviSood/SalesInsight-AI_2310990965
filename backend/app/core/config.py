"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # App
    APP_NAME: str = "SalesInsight AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    # File upload
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: str = ".csv,.xlsx,.xls"

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 20
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # AI Engine — supports "groq" or "gemini"
    AI_PROVIDER: str = "groq"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Email — supports "resend" or "smtp"
    EMAIL_PROVIDER: str = "resend"
    RESEND_API_KEY: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "insights@salesinsight.ai"
    EMAIL_FROM_NAME: str = "SalesInsight AI"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def allowed_extensions_list(self) -> list[str]:
        return [e.strip().lower() for e in self.ALLOWED_EXTENSIONS.split(",") if e.strip()]

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
