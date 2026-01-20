import { NextRequest, NextResponse } from "next/server";
import { markTaskComplete } from "./mark-task-complete";
import { markTaskIncomplete } from "./mark-task-incomplete";

// POST /api/order-tasks/{id}/complete
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id: task_id } = await params;

  // TODO: Get authenticated user ID and role from session/token
  // For now, use placeholder values - this should be replaced with actual auth
  const authenticatedUserId = "00000000-0000-0000-0000-000000000000";
  const isStaff = true; // Assume staff for now

  const result = await markTaskComplete(task_id, authenticatedUserId, isStaff);

  if (result.error) {
    return NextResponse.json({ error: result.error }, { status: result.status });
  }

  return NextResponse.json(result.data, { status: 200 });
}

// DELETE /api/order-tasks/{id}/complete
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id: task_id } = await params;

  // TODO: Get authenticated user role from session/token
  // For now, assume staff - this should be replaced with actual auth
  const isStaff = true;

  const result = await markTaskIncomplete(task_id, isStaff);

  if (result.error) {
    return NextResponse.json({ error: result.error }, { status: result.status });
  }

  return NextResponse.json(result.data, { status: 200 });
}
