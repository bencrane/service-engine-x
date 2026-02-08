"""Authentication dependencies for FastAPI."""

from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import Depends, Header, HTTPException, status

from app.auth.utils import extract_bearer_token, hash_token
from app.database import get_supabase


@dataclass
class AuthContext:
    """Authentication context containing org and user info."""

    org_id: str
    user_id: str
    token_id: str


async def get_current_org(
    authorization: str | None = Header(None, alias="Authorization"),
) -> AuthContext:
    """
    Validate API token and return authentication context.

    Raises HTTPException 401 if token is invalid or expired.
    """
    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    token_hash = hash_token(token)
    supabase = get_supabase()

    # Look up token by hash
    result = (
        supabase.table("api_tokens")
        .select("id, user_id, org_id, expires_at")
        .eq("token_hash", token_hash)
        .execute()
    )

    if not result.data or len(result.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    token_data = result.data[0]

    # Check expiration
    if token_data.get("expires_at"):
        expires_at = datetime.fromisoformat(token_data["expires_at"].replace("Z", "+00:00"))
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )

    # Update last_used_at
    supabase.table("api_tokens").update(
        {"last_used_at": datetime.now(timezone.utc).isoformat()}
    ).eq("id", token_data["id"]).execute()

    return AuthContext(
        org_id=token_data["org_id"],
        user_id=token_data["user_id"],
        token_id=token_data["id"],
    )
