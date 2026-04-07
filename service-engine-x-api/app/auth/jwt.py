"""JWT token creation and validation for user session auth."""

from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings


def create_access_token(user_id: str, org_id: str, role_id: str) -> str:
    """
    Create a signed JWT access token for a user session.

    Payload:
        sub: user_id
        org_id: organization the user belongs to
        role_id: user's role (Client vs Administrator)
        iat: issued at
        exp: expiration
        type: "session" (distinguishes from API tokens)
    """
    now = datetime.now(timezone.utc)

    payload = {
        "sub": user_id,
        "org_id": org_id,
        "role_id": role_id,
        "iat": now,
        "exp": now + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
        "type": "session",
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Returns the payload dict on success.
    Raises jwt.ExpiredSignatureError if expired.
    Raises jwt.InvalidTokenError for any other validation failure.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
