"""Public orgs list — used by the frontend to populate its org picker."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth import verify_token_or_internal_bearer
from app.database import get_supabase

router = APIRouter(prefix="/api/orgs", tags=["Orgs"])


class OrgListItem(BaseModel):
    id: str
    name: str
    slug: str
    domain: str | None


@router.get("", dependencies=[Depends(verify_token_or_internal_bearer)])
async def list_orgs() -> list[OrgListItem]:
    result = (
        get_supabase()
        .table("organizations")
        .select("id, name, slug, domain")
        .order("name")
        .execute()
    )
    return [OrgListItem(**org) for org in (result.data or [])]
