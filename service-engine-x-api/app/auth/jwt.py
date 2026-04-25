"""JWT verification via auth-engine-x JWKS endpoint.

EdDSA JWTs are verified against the JWKS published by auth-engine-x. Issuer,
audience, and JWKS URL are read from settings; signing keys are cached for
five minutes by ``PyJWKClient``.
"""

import jwt
from jwt import PyJWKClient

from app.config import settings

_jwks_client = PyJWKClient(
    settings.AUX_JWKS_URL,
    cache_jwk_set=True,
    lifespan=300,  # 5-minute cache
)


def _decode_token(token: str, expected_type: str) -> dict | None:
    """Verify a JWT against the JWKS endpoint and check the ``type`` claim.

    Returns the payload dict if valid, ``None`` otherwise.
    """
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["EdDSA"],
            issuer=settings.AUX_ISSUER,
            audience=settings.AUX_AUDIENCE,
            options={"require": ["exp", "sub"]},
        )
        if payload.get("type") != expected_type:
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None


def decode_access_token(token: str) -> dict | None:
    """Decode and validate a session JWT. Returns payload or ``None``."""
    return _decode_token(token, "session")


def decode_m2m_token(token: str) -> dict | None:
    """Decode and validate an M2M JWT. Returns payload or ``None``."""
    return _decode_token(token, "m2m")
