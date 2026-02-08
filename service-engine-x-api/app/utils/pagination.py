"""Pagination utility functions."""

from typing import Any

from app.models.common import PaginatedResponse, PaginationLinks, PaginationMeta


def build_pagination_response(
    data: list[Any],
    total: int,
    page: int,
    limit: int,
    path: str,
) -> dict[str, Any]:
    """
    Build a paginated response matching the Next.js API format.

    Args:
        data: List of items for the current page
        total: Total count of all items
        page: Current page number (1-indexed)
        limit: Items per page
        path: Base URL path for pagination links

    Returns:
        Dictionary with data, links, and meta
    """
    last_page = max(1, (total + limit - 1) // limit)
    offset = (page - 1) * limit

    links = PaginationLinks(
        first=f"{path}?page=1&limit={limit}",
        last=f"{path}?page={last_page}&limit={limit}",
        prev=f"{path}?page={page - 1}&limit={limit}" if page > 1 else None,
        next=f"{path}?page={page + 1}&limit={limit}" if page < last_page else None,
    )

    meta = PaginationMeta(
        current_page=page,
        from_=offset + 1 if total > 0 else 0,
        to=min(offset + limit, total),
        last_page=last_page,
        per_page=limit,
        total=total,
        path=path,
    )

    return {
        "data": data,
        "links": links.model_dump(),
        "meta": meta.model_dump(by_alias=True),
    }
