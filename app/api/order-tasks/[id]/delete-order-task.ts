import { supabase } from "@/lib/supabase";

export async function deleteOrderTask(
  task_id: string
): Promise<{ error?: string; status: number }> {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

  // Validate UUID format
  if (!uuidRegex.test(task_id)) {
    return { error: "Not Found", status: 404 };
  }

  // Get existing task with order info
  const { data: task, error: fetchError } = await supabase
    .from("order_tasks")
    .select(`
      id,
      order_id,
      orders!inner (
        id,
        deleted_at
      )
    `)
    .eq("id", task_id)
    .single();

  if (fetchError || !task) {
    return { error: "Not Found", status: 404 };
  }

  // Check if parent order is soft-deleted
  const order = task.orders as unknown as { id: string; deleted_at: string | null };
  if (order?.deleted_at) {
    return { error: "Not Found", status: 404 };
  }

  // Delete employee assignments first (in case cascade isn't set)
  await supabase
    .from("order_task_employees")
    .delete()
    .eq("order_task_id", task_id);

  // Hard delete the task
  const { error: deleteError } = await supabase
    .from("order_tasks")
    .delete()
    .eq("id", task_id);

  if (deleteError) {
    console.error("Failed to delete order task:", deleteError);
    return { error: "Internal server error", status: 500 };
  }

  // Update order.updated_at
  await supabase
    .from("orders")
    .update({ updated_at: new Date().toISOString() })
    .eq("id", task.order_id);

  return { status: 204 };
}
