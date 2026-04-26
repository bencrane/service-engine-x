"""Pydantic settings (env vars).

Auth foundation (AUX_*) is inherited from ``aux_m2m_server.BaseAuthSettings``.
Do not redeclare ``AUX_JWKS_URL`` / ``AUX_ISSUER`` / ``AUX_AUDIENCE`` /
``AUX_API_BASE_URL`` / ``AUX_M2M_API_KEY`` here — they're owned upstream so
every AUX backend uses identical field names and the same boot-required
contract.
"""

from aux_m2m_server import BaseAuthSettings


class Settings(BaseAuthSettings):
    # Supabase
    SERVICE_ENGINE_X_SUPABASE_URL: str
    SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY: str

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # API
    SERX_API_BASE_URL: str
    DEBUG: bool = False
    APP_NAME: str = "Service Engine X API"
    APP_VERSION: str = "1.0.0"

    # Managed agents dispatch (used by scheduler endpoint).
    # Outbound auth to OPEX is handled by ``aux_m2m_client.AsyncM2MAuth`` —
    # there is no longer a static ``OPEX_AUTH_TOKEN`` in this config.
    OPEX_API_URL: str = ""

    # Scheduler windows — all overridable via env
    SCHEDULER_PREFRAME_WINDOW_START_HOURS: int = 4
    SCHEDULER_PREFRAME_WINDOW_END_HOURS: int = 5
    SCHEDULER_PREFRAME_MIN_AGE_HOURS: int = 2
    SCHEDULER_MAX_DISPATCH_ATTEMPTS: int = 5
    SCHEDULER_DISPATCH_TIMEOUT_SECONDS: float = 15.0

    # Third-party
    RESEND_API_KEY: str = ""
    DOCRAPTOR_API_KEY: str = ""
    CAL_API_KEY: str = ""
    CALCOM_BASE_URL: str = "https://api.cal.com"
    CALCOM_API_VERSION: str = "2024-06-14"
    CALCOM_EVENT_TYPE_CACHE_TTL_SECONDS: int = 86400
    CAL_WEBHOOK_SECRET: str = ""


settings = Settings()  # type: ignore[call-arg]
