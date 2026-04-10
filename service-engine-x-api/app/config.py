from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Supabase
    SERVICE_ENGINE_X_SUPABASE_URL: str
    SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY: str

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 72

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # API
    API_BASE_URL: str = "http://localhost:8000"
    DEBUG: bool = False
    APP_NAME: str = "Service Engine X API"
    APP_VERSION: str = "1.0.0"

    # Internal
    INTERNAL_API_KEY: str = ""

    # Third-party
    RESEND_API_KEY: str = ""
    DOCRAPTOR_API_KEY: str = ""
    CAL_API_KEY: str = ""
    CALCOM_BASE_URL: str = "https://api.cal.com"
    CALCOM_API_VERSION: str = "2024-06-14"
    CALCOM_EVENT_TYPE_CACHE_TTL_SECONDS: int = 86400


settings = Settings()  # type: ignore[call-arg]
