import { supabase } from "@/lib/supabase";

interface CreateOrderTaskInput {
  name: string;
  description?: string | null;
  employee_ids?: string[];
  sort_order?: number;
  is_public?: boolean;
  for_client?: boolean;
  deadline?: number | null;
  due_at?: string | null;
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

interface ValidationErrors {
  [key: string]: string[];
}

export async function createOrderTask(
  order_id: string,
  input: CreateOrderTaskInput
): Promise<{ data?: OrderTask; error?: string; errors?: ValidationErrors; status: number }> {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

  // Validate UUID format for order_id
  if (!uuidRegex.test(order_id)) {
    return { error: "Not Found", status: 404 };
  }

  // Validate required fields
  const errors: ValidationErrors = {};

  if (!input.name || typeof input.name !== "string" || input.name.trim() === "") {
    errors.name = ["The name field is required."];
  }

  // Validate employee_ids format
  const employeeIds = input.employee_ids || [];
  if (!Array.isArray(employeeIds)) {
    errors.employee_ids = ["The employee_ids field must be an array."];
  } else {
    for (const id of employeeIds) {
      if (!uuidRegex.test(id)) {
        errors.employee_ids = ["All employee_ids must be valid UUIDs."];
        break;
      }
    }
  }

  // Validate for_client + employee_ids mutual exclusion
  const forClient = input.for_client ?? false;
  if (forClient && employeeIds.length > 0) {
    errors.for_client = ["Cannot assign employees when for_client is true."];
  }

  // Validate deadline + due_at mutual exclusion
  const hasDeadline = input.deadline !== undefined && input.deadline !== null;
  const hasDueAt = input.due_at !== undefined && input.due_at !== null;
  if (hasDeadline && hasDueAt) {
    errors.deadline = ["deadline and due_at are mutually exclusive."];
  }

  if (Object.keys(errors).length > 0) {
    return {
      error: "The given data was invalid.",
      errors,
      status: 400,
    };
  }

  // Check if order exists and is not soft-deleted
  const { data: order, error: orderError } = await supabase
    .from("orders")
    .select("id")
    .eq("id", order_id)
    .is("deleted_at", null)
    .single();

  if (orderError || !order) {
    return { error: "Not Found", status: 404 };
  }

  // Validate employee_ids exist
  if (employeeIds.length > 0) {
    const { data: users, error: usersError } = await supabase
      .from("users")
      .select("id")
      .in("id", employeeIds);

    if (usersError) {
      return { error: "Internal server error", status: 500 };
    }

    const foundIds = new Set((users || []).map((u) => u.id));
    const missingIds = employeeIds.filter((id) => !foundIds.has(id));

    if (missingIds.length > 0) {
      return {
        error: "The given data was invalid.",
        errors: { employee_ids: [`Employee with ID ${missingIds[0]} does not exist.`] },
        status: 422,
      };
    }
  }

  // Prepare task data
  const taskData = {
    order_id,
    name: input.name.trim(),
    description: input.description ?? null,
    sort_order: input.sort_order ?? 0,
    is_public: input.is_public ?? false,
    for_client: forClient,
    is_complete: false,
    completed_by: null,
    completed_at: null,
    deadline: hasDeadline ? input.deadline : null,
    due_at: hasDueAt ? input.due_at : null,
  };

  // Insert task
  const { data: newTask, error: insertError } = await supabase
    .from("order_tasks")
    .insert(taskData)
    .select("id, order_id, name, description, sort_order, is_public, for_client, is_complete, completed_by, completed_at, deadline, due_at")
    .single();

  if (insertError) {
    console.error("Failed to create order task:", insertError);
    return { error: "Internal server error", status: 500 };
  }

  // Insert employee assignments
  let employees: Employee[] = [];
  if (employeeIds.length > 0) {
    const assignmentRows = employeeIds.map((user_id) => ({
      order_task_id: newTask.id,
      user_id,
    }));

    const { error: assignError } = await supabase
      .from("order_task_employees")
      .insert(assignmentRows);

    if (assignError) {
      console.error("Failed to assign employees:", assignError);
      // Don't fail the request, task was created
    }

    // Fetch employee details for response
    const { data: users } = await supabase
      .from("users")
      .select("id, name_f, name_l")
      .in("id", employeeIds);

    employees = (users || []).map((u) => ({
      id: u.id,
      name_f: u.name_f,
      name_l: u.name_l,
    }));
  }

  // Update order.updated_at
  await supabase
    .from("orders")
    .update({ updated_at: new Date().toISOString() })
    .eq("id", order_id);

  return {
    data: {
      id: newTask.id,
      order_id: newTask.order_id,
      name: newTask.name,
      description: newTask.description,
      sort_order: newTask.sort_order,
      is_public: newTask.is_public,
      for_client: newTask.for_client,
      is_complete: newTask.is_complete,
      completed_by: newTask.completed_by,
      completed_at: newTask.completed_at,
      deadline: newTask.deadline,
      due_at: newTask.due_at,
      employees,
    },
    status: 201,
  };
}
