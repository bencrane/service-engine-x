import { NextRequest, NextResponse } from "next/server";
import { deleteOrderMessage } from "./delete-order-message";

// DELETE /api/order-messages/{id}
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  const result = await deleteOrderMessage(id);

  if (result.error) {
    return NextResponse.json({ error: result.error }, { status: result.status });
  }

  return new NextResponse(null, { status: 204 });
}
