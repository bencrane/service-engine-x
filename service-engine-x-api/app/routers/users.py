"""Public users list — used by the frontend to populate its user picker."""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.auth import verify_token
from app.database import get_supabase

router = APIRouter(prefix="/api/users", tags=["Users"])


class UserListItem(BaseModel):
    id: str
    email: str
    name_f: str
    name_l: str
    org_id: str


@router.get("", dependencies=[Depends(verify_token)])
async def list_users(
    org_id: str | None = Query(None, description="Optional: filter users by org"),
) -> list[UserListItem]:
    query = (
        get_supabase()
        .table("users")
        .select("id, email, name_f, name_l, org_id")
        .order("email")
    )
    if org_id:
        query = query.eq("org_id", org_id)
    result = query.execute()
    return [UserListItem(**u) for u in (result.data or [])]
