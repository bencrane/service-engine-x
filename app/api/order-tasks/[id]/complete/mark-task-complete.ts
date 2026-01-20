import { supabase } from "@/lib/supabase";

interface Employee {
  id: string;
  name_f: string | null;
  name_l: string | null;
}

interface OrderTask {
  id: string;
  order_id: string;
  name: string;
  description: string | null;
  sort_order: number;
  is_public: boolean;
  for_client: boolean;
  is_complete: boolean;
  completed_by: string | null;
  completed_at: string | null;
  deadline: number | null;
  due_at: string | null;
  employees: Employee[];
}

export async function markTaskComplete(
  task_id: string,
  authenticatedUserId: string,
  isStaff: boolean
): Promise<{ data?: OrderTask; error?: string; status: number }> {
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
      name,
      description,
      sort_order,
      is_public,
      for_client,
      is_complete,
      completed_by,
      completed_at,
      deadline,
      due_at,
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

  // Check permissions: clients can only complete for_client tasks
  if (!isStaff && !task.for_client) {
    return { error: "Forbidden", status: 403 };
  }

  // If already complete, return current state (idempotent)
  if (task.is_complete) {
    // Fetch employees for response
    const employees = await fetchTaskEmployees(task_id);

    return {
      data: {
        id: task.id,
        order_id: task.order_id,
        name: task.name,
        description: task.description,
        sort_order: task.sort_order,
        is_public: task.is_public,
        for_client: task.for_client,
        is_complete: task.is_complete,
        completed_by: task.completed_by,
        completed_at: task.completed_at,
        deadline: task.deadline,
        due_at: task.due_at,
        employees,
      },
      status: 200,
    };
  }

  // Mark complete
  const now = new Date().toISOString();
  const { data: updatedTask, error: updateError } = await supabase
    .from("order_tasks")
    .update({
      is_complete: true,
      completed_by: authenticatedUserId,
      completed_at: now,
      updated_at: now,
    })
    .eq("id", task_id)
    .select("id, order_id, name, description, sort_order, is_public, for_client, is_complete, completed_by, completed_at, deadline, due_at")
    .single();

  if (updateError) {
    console.error("Failed to mark task complete:", updateError);
    return { error: "Internal server error", status: 500 };
  }

  // Update order.updated_at
  await supabase
    .from("orders")
    .update({ updated_at: now })
    .eq("id", updatedTask.order_id);

  // Fetch employees for response
  const employees = await fetchTaskEmployees(task_id);

  return {
    data: {
      id: updatedTask.id,
      order_id: updatedTask.order_id,
      name: updatedTask.name,
      description: updatedTask.description,
      sort_order: updatedTask.sort_order,
      is_public: updatedTask.is_public,
      for_client: updatedTask.for_client,
      is_complete: updatedTask.is_complete,
      completed_by: updatedTask.completed_by,
      completed_at: updatedTask.completed_at,
      deadline: updatedTask.deadline,
      due_at: updatedTask.due_at,
      employees,
    },
    status: 200,
  };
}

async function fetchTaskEmployees(task_id: string): Promise<Employee[]> {
  const { data: assignments } = await supabase
    .from("order_task_employees")
    .select(`
      user_id,
      users:user_id (
        id,
        name_f,
        name_l
      )
    `)
    .eq("order_task_id", task_id);

  const employees: Employee[] = [];
  if (assignments) {
    for (const a of assignments) {
      const user = a.users as unknown as { id: string; name_f: string | null; name_l: string | null } | null;
      if (user) {
        employees.push({
          id: user.id,
          name_f: user.name_f,
          name_l: user.name_l,
        });
      }
    }
  }
  return employees;
}
