"""Validation utility functions."""

import re

UUID_REGEX = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def is_valid_uuid(value: str) -> bool:
    """Check if a string is a valid UUID."""
    return bool(UUID_REGEX.match(value))


def validate_email(email: str) -> bool:
    """Check if a string is a valid email address."""
    return bool(EMAIL_REGEX.match(email))
