import { supabase } from "@/lib/supabase";

interface ListOrderTasksParams {
  order_id: string;
  limit?: number;
  page?: number;
}

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

interface PaginatedResponse {
  data: OrderTask[];
  links: {
    first: string;
    last: string;
    prev: string | null;
    next: string | null;
  };
  meta: {
    current_page: number;
    from: number;
    to: number;
    last_page: number;
    per_page: number;
    total: number;
    path: string;
  };
}

export async function listOrderTasks(
  params: ListOrderTasksParams,
  baseUrl: string,
  orgId: string
): Promise<{ data?: PaginatedResponse; error?: string; status: number }> {
  const { order_id, limit = 20, page = 1 } = params;

  // Validate UUID format
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(order_id)) {
    return { error: "Not Found", status: 404 };
  }

  // Validate pagination params
  const validLimit = Math.max(1, Math.min(100, limit));
  const validPage = Math.max(1, page);
  const offset = (validPage - 1) * validLimit;

  // Check if order exists and is not soft-deleted
  const { data: order, error: orderError } = await supabase
    .from("orders")
    .select("id")
    .eq("id", order_id)
    .eq("org_id", orgId)
    .is("deleted_at", null)
    .single();

  if (orderError || !order) {
    return { error: "Not Found", status: 404 };
  }

  // Get total count
  const { count, error: countError } = await supabase
    .from("order_tasks")
    .select("*", { count: "exact", head: true })
    .eq("order_id", order_id);

  if (countError) {
    return { error: "Internal server error", status: 500 };
  }

  const total = count || 0;
  const lastPage = Math.ceil(total / validLimit) || 1;

  // Get tasks (sorted by created_at descending)
  const { data: tasks, error: tasksError } = await supabase
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
      due_at
    `)
    .eq("order_id", order_id)
    .order("created_at", { ascending: false })
    .range(offset, offset + validLimit - 1);

  if (tasksError) {
    return { error: "Internal server error", status: 500 };
  }

  // Fetch employee assignments for all tasks
  const taskIds = (tasks || []).map((t) => t.id);
  let employeeMap: Record<string, Employee[]> = {};

  if (taskIds.length > 0) {
    const { data: assignments, error: assignError } = await supabase
      .from("order_task_employees")
      .select(`
        order_task_id,
        user_id,
        users:user_id (
          id,
          name_f,
          name_l
        )
      `)
      .in("order_task_id", taskIds);

    if (!assignError && assignments) {
      for (const a of assignments) {
        if (!employeeMap[a.order_task_id]) {
          employeeMap[a.order_task_id] = [];
        }
        const user = a.users as unknown as { id: string; name_f: string | null; name_l: string | null } | null;
        if (user) {
          employeeMap[a.order_task_id].push({
            id: user.id,
            name_f: user.name_f,
            name_l: user.name_l,
          });
        }
      }
    }
  }

  const path = `${baseUrl}/api/orders/${order_id}/tasks`;

  const response: PaginatedResponse = {
    data: (tasks || []).map((t) => ({
      id: t.id,
      order_id: t.order_id,
      name: t.name,
      description: t.description,
      sort_order: t.sort_order,
      is_public: t.is_public,
      for_client: t.for_client,
      is_complete: t.is_complete,
      completed_by: t.completed_by,
      completed_at: t.completed_at,
      deadline: t.deadline,
      due_at: t.due_at,
      employees: employeeMap[t.id] || [],
    })),
    links: {
      first: `${path}?page=1&limit=${validLimit}`,
      last: `${path}?page=${lastPage}&limit=${validLimit}`,
      prev: validPage > 1 ? `${path}?page=${validPage - 1}&limit=${validLimit}` : null,
      next: validPage < lastPage ? `${path}?page=${validPage + 1}&limit=${validLimit}` : null,
    },
    meta: {
      current_page: validPage,
      from: total > 0 ? offset + 1 : 0,
      to: Math.min(offset + validLimit, total),
      last_page: lastPage,
      per_page: validLimit,
      total,
      path,
    },
  };

  return { data: response, status: 200 };
}
