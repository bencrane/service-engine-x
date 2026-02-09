"""Formatting utility functions for API response serialization."""

from typing import Any


def format_currency(value: Any, default: str = "0.00") -> str:
    """
    Format a value as a two-decimal currency string.

    Handles float, int, str, Decimal, and None from the database.
    Always returns a consistently formatted string like "0.00", "125.50", etc.
    """
    if value is None:
        return default
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return default


def format_currency_optional(value: Any) -> str | None:
    """
    Format a value as a two-decimal currency string, returning None if the value is None.

    Use this for nullable currency fields where None has semantic meaning
    (e.g., tax not set vs. tax = 0).
    """
    if value is None:
        return None
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return None
