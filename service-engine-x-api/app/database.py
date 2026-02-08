"""Supabase client initialization."""

from functools import lru_cache

from supabase import Client, create_client

from app.config import get_settings


@lru_cache
def get_supabase() -> Client:
    """Get cached Supabase client instance."""
    settings = get_settings()
    return create_client(
        settings.service_engine_x_supabase_url,
        settings.service_engine_x_supabase_service_role_key,
    )


# Convenience alias for direct imports
supabase = get_supabase
