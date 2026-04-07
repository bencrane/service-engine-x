"""Supabase client initialization."""

from functools import lru_cache

from supabase import Client, create_client

from app.config import settings


@lru_cache
def get_supabase() -> Client:
    """Get cached Supabase client instance."""
    return create_client(
        settings.SERVICE_ENGINE_X_SUPABASE_URL,
        settings.SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY,
    )


# Convenience alias for direct imports
supabase = get_supabase
