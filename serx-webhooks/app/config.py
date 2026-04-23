from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Supabase (Doppler-injected)
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Cal.com webhook HMAC — empty means skip verification and log warning
    CAL_WEBHOOK_SECRET: str = ""

    # managed-agents-x-api dispatch. Empty OPEX_AUTH_TOKEN disables dispatch
    # (rows marked 'dispatch_disabled') so local dev / tests run without
    # the secret. Dispatch runs out-of-band inside the existing ingest
    # BackgroundTask — upstream 202 does not wait on it.
    OPEX_API_URL: str = "https://api.managedagents.run"
    OPEX_AUTH_TOKEN: str = ""
    OPEX_DISPATCH_ENABLED: bool = True
    OPEX_DISPATCH_TIMEOUT_SECONDS: float = 10.0
    OPEX_DISPATCH_MAX_ATTEMPTS: int = 3

    # Runtime
    PORT: int = 8000
    DEBUG: bool = False
    APP_NAME: str = "serx-webhooks"
    APP_VERSION: str = "0.1.0"

    # CORS — permissive for phase 1
    CORS_ORIGINS: list[str] = ["*"]


settings = Settings()  # type: ignore[call-arg]
