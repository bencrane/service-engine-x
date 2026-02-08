import { NextRequest, NextResponse } from "next/server";
import { listOrderTasks } from "./list-order-tasks";
import { createOrderTask } from "./create-order-task";
import { validateApiToken, extractBearerToken } from "@/lib/auth";

// GET /api/orders/{id}/tasks
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const token = extractBearerToken(request.headers.get("authorization"));
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const auth = await validateApiToken(token);
  if (!auth.valid || !auth.orgId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { id: order_id } = await params;
  const { searchParams } = new URL(request.url);

  const limit = parseInt(searchParams.get("limit") || "20", 10);
  const page = parseInt(searchParams.get("page") || "1", 10);

  const baseUrl = new URL(request.url).origin;

  const result = await listOrderTasks({ order_id, limit, page }, baseUrl, auth.orgId);

  if (result.error) {
    return NextResponse.json({ error: result.error }, { status: result.status });
  }

  return NextResponse.json(result.data, { status: 200 });
}

// POST /api/orders/{id}/tasks
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const token = extractBearerToken(request.headers.get("authorization"));
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const auth = await validateApiToken(token);
  if (!auth.valid || !auth.orgId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

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

  const result = await createOrderTask(order_id, body, auth.orgId);

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
