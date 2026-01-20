import { NextRequest, NextResponse } from "next/server";
import { listOrderMessages } from "./list-order-messages";
import { createOrderMessage } from "./create-order-message";

// GET /api/orders/{id}/messages
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id: order_id } = await params;
  const { searchParams } = new URL(request.url);

  const limit = parseInt(searchParams.get("limit") || "20", 10);
  const page = parseInt(searchParams.get("page") || "1", 10);

  const baseUrl = new URL(request.url).origin;

  const result = await listOrderMessages({ order_id, limit, page }, baseUrl);

  if (result.error) {
    return NextResponse.json({ error: result.error }, { status: result.status });
  }

  return NextResponse.json(result.data, { status: 200 });
}

// POST /api/orders/{id}/messages
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id: order_id } = await params;

  let body;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      { error: "Invalid JSON body" },
      { status: 400 }
    );
  }

  // TODO: Get authenticated user ID from session/token
  // For now, use a placeholder - this should be replaced with actual auth
  const authenticatedUserId = body.user_id || "00000000-0000-0000-0000-000000000000";

  const result = await createOrderMessage(order_id, body, authenticatedUserId);

  if (result.error) {
    const response: { error?: string; message?: string; errors?: Record<string, string[]> } = {};
    
    if (result.errors) {
      response.message = result.error;
      response.errors = result.errors;
    } else {
      response.error = result.error;
    }
    
    return NextResponse.json(response, { status: result.status });
  }

  return NextResponse.json(result.data, { status: 201 });
}
