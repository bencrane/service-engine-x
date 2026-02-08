"""Order Messages API router for standalone message operations."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from app.auth import AuthContext, get_current_org
from app.database import get_supabase
from app.utils import is_valid_uuid

router = APIRouter(prefix="/api/order-messages", tags=["Order Messages"])


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_message(
    message_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> Response:
    """Delete an order message."""
    if not is_valid_uuid(message_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Get message with order verification
    result = (
        supabase.table("order_messages")
        .select("*, orders!inner(id, org_id, deleted_at)")
        .eq("id", message_id)
        .execute()
    )

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    message = result.data[0]
    order = message.get("orders")
    if isinstance(order, list):
        order = order[0] if order else None

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Check org_id and deleted_at
    if order.get("org_id") != auth.org_id or order.get("deleted_at") is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Delete message
    supabase.table("order_messages").delete().eq("id", message_id).execute()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
