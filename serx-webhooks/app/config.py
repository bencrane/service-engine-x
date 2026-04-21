from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Supabase (Doppler-injected)
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Cal.com webhook HMAC — empty means skip verification and log warning
    CAL_WEBHOOK_SECRET: str = ""

    # Runtime
    PORT: int = 8000
    DEBUG: bool = False
    APP_NAME: str = "serx-webhooks"
    APP_VERSION: str = "0.1.0"

    # CORS — permissive for phase 1
    CORS_ORIGINS: list[str] = ["*"]


settings = Settings()  # type: ignore[call-arg]
