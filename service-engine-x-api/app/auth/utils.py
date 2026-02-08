"""Authentication utility functions."""

from hashlib import sha256


def hash_token(token: str) -> str:
    """Hash an API token using SHA-256."""
    return sha256(token.encode()).hexdigest()


def extract_bearer_token(authorization: str | None) -> str | None:
    """Extract token from Bearer authorization header."""
    if not authorization:
        return None
    if not authorization.startswith("Bearer "):
        return None
    return authorization[7:]
