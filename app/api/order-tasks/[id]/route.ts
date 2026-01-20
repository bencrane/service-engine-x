import { NextRequest, NextResponse } from "next/server";
import { updateOrderTask } from "./update-order-task";
import { deleteOrderTask } from "./delete-order-task";

// PUT /api/order-tasks/{id}
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id: task_id } = await params;

  let body;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      { error: "Invalid JSON body" },
      { status: 400 }
    );
  }

  const result = await updateOrderTask(task_id, body);

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

  return NextResponse.json(result.data, { status: 200 });
}

// DELETE /api/order-tasks/{id}
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id: task_id } = await params;

  const result = await deleteOrderTask(task_id);

  if (result.error) {
    return NextResponse.json({ error: result.error }, { status: result.status });
  }

  return new NextResponse(null, { status: 204 });
}
