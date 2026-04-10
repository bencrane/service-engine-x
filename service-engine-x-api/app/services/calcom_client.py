"""Cal.com API client for internal integrations."""

import asyncio
from typing import Any

import httpx


class CalcomClientError(Exception):
    """Base Cal.com API client error."""


class CalcomNotFoundError(CalcomClientError):
    """Raised when a Cal.com resource cannot be found."""


class CalcomClient:
    """Thin Cal.com v2 API client with retry support."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.cal.com",
        api_version: str = "2024-06-14",
        max_retries: int = 3,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._api_version = api_version
        self._max_retries = max_retries

    async def get_event_type(self, event_type_id: int) -> dict[str, Any]:
        """Fetch a Cal.com event type by ID."""
        url = f"{self._base_url}/v2/event-types/{event_type_id}"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "cal-api-version": self._api_version,
        }

        backoff_seconds = 1.0
        last_error: Exception | None = None

        async with httpx.AsyncClient(timeout=15.0) as client:
            for attempt in range(self._max_retries):
                try:
                    response = await client.get(url, headers=headers)

                    if response.status_code == 404:
                        raise CalcomNotFoundError(f"Event type {event_type_id} was not found")

                    if response.status_code == 429:
                        if attempt == self._max_retries - 1:
                            raise CalcomClientError("Cal.com rate limit reached")
                        await asyncio.sleep(backoff_seconds)
                        backoff_seconds *= 2
                        continue

                    response.raise_for_status()
                    return response.json()
                except httpx.RequestError as exc:
                    last_error = exc
                    if attempt == self._max_retries - 1:
                        break
                    await asyncio.sleep(backoff_seconds)
                    backoff_seconds *= 2
                except httpx.HTTPStatusError as exc:
                    raise CalcomClientError(
                        f"Cal.com returned {exc.response.status_code}: {exc.response.text}"
                    ) from exc

        raise CalcomClientError(f"Cal.com request failed: {last_error}")
