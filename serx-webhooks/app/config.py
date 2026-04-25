from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Every field is required — Doppler is the sole source of env. No fallbacks.
    SERX_SUPABASE_URL: str
    SERX_SUPABASE_SERVICE_ROLE_KEY: str

    CAL_WEBHOOK_SECRET: str

    OPEX_API_BASE_URL: str
    OPEX_AUTH_TOKEN: str
    OPEX_DISPATCH_ENABLED: bool
    OPEX_DISPATCH_TIMEOUT_SECONDS: float
    OPEX_DISPATCH_MAX_ATTEMPTS: int

    DEBUG: bool
    APP_NAME: str
    APP_VERSION: str
    CORS_ORIGINS: list[str]


settings = Settings()  # type: ignore[call-arg]
