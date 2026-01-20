import { supabase } from "@/lib/supabase";

interface UpdateOrderTaskInput {
  name?: string;
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

export async function updateOrderTask(
  task_id: string,
  input: UpdateOrderTaskInput
): Promise<{ data?: OrderTask; error?: string; errors?: ValidationErrors; status: number }> {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

  // Validate UUID format
  if (!uuidRegex.test(task_id)) {
    return { error: "Not Found", status: 404 };
  }

  // Get existing task
  const { data: existingTask, error: fetchError } = await supabase
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

  if (fetchError || !existingTask) {
    return { error: "Not Found", status: 404 };
  }

  // Check if parent order is soft-deleted
  const order = existingTask.orders as unknown as { id: string; deleted_at: string | null };
  if (order?.deleted_at) {
    return { error: "Not Found", status: 404 };
  }

  // Validate input
  const errors: ValidationErrors = {};

  if (input.name !== undefined && (typeof input.name !== "string" || input.name.trim() === "")) {
    errors.name = ["The name field cannot be empty."];
  }

  // Validate employee_ids format
  const employeeIds = input.employee_ids;
  const hasEmployeeIds = employeeIds !== undefined;
  if (hasEmployeeIds) {
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
  }

  // Determine resulting for_client value
  const resultingForClient = input.for_client ?? existingTask.for_client;
  const resultingEmployeeIds = hasEmployeeIds ? employeeIds : null; // null = not changing

  // Validate for_client + employee_ids mutual exclusion
  if (resultingForClient && hasEmployeeIds && employeeIds!.length > 0) {
    errors.for_client = ["Cannot assign employees when for_client is true."];
  }

  // Validate deadline + due_at mutual exclusion
  const hasDeadlineInInput = input.deadline !== undefined;
  const hasDueAtInInput = input.due_at !== undefined;
  
  const resultingDeadline = hasDeadlineInInput ? input.deadline : existingTask.deadline;
  const resultingDueAt = hasDueAtInInput ? input.due_at : existingTask.due_at;

  if (resultingDeadline !== null && resultingDueAt !== null) {
    errors.deadline = ["deadline and due_at are mutually exclusive."];
  }

  if (Object.keys(errors).length > 0) {
    return {
      error: "The given data was invalid.",
      errors,
      status: 400,
    };
  }

  // Validate employee_ids exist if provided
  if (hasEmployeeIds && employeeIds!.length > 0) {
    const { data: users, error: usersError } = await supabase
      .from("users")
      .select("id")
      .in("id", employeeIds!);

    if (usersError) {
      return { error: "Internal server error", status: 500 };
    }

    const foundIds = new Set((users || []).map((u) => u.id));
    const missingIds = employeeIds!.filter((id) => !foundIds.has(id));

    if (missingIds.length > 0) {
      return {
        error: "The given data was invalid.",
        errors: { employee_ids: [`Employee with ID ${missingIds[0]} does not exist.`] },
        status: 422,
      };
    }
  }

  // Build update object (only include provided fields)
  const updateData: Record<string, unknown> = {
    updated_at: new Date().toISOString(),
  };

  if (input.name !== undefined) updateData.name = input.name.trim();
  if (input.description !== undefined) updateData.description = input.description;
  if (input.sort_order !== undefined) updateData.sort_order = input.sort_order;
  if (input.is_public !== undefined) updateData.is_public = input.is_public;
  if (input.for_client !== undefined) updateData.for_client = input.for_client;
  if (hasDeadlineInInput) updateData.deadline = input.deadline;
  if (hasDueAtInInput) updateData.due_at = input.due_at;

  // Update task
  const { data: updatedTask, error: updateError } = await supabase
    .from("order_tasks")
    .update(updateData)
    .eq("id", task_id)
    .select("id, order_id, name, description, sort_order, is_public, for_client, is_complete, completed_by, completed_at, deadline, due_at")
    .single();

  if (updateError) {
    console.error("Failed to update order task:", updateError);
    return { error: "Internal server error", status: 500 };
  }

  // Handle employee_ids replacement (full replacement, no merge)
  let employees: Employee[] = [];
  if (hasEmployeeIds) {
    // Delete existing assignments
    await supabase
      .from("order_task_employees")
      .delete()
      .eq("order_task_id", task_id);

    // Insert new assignments
    if (employeeIds!.length > 0) {
      const assignmentRows = employeeIds!.map((user_id) => ({
        order_task_id: task_id,
        user_id,
      }));

      await supabase
        .from("order_task_employees")
        .insert(assignmentRows);

      // Fetch employee details for response
      const { data: users } = await supabase
        .from("users")
        .select("id, name_f, name_l")
        .in("id", employeeIds!);

      employees = (users || []).map((u) => ({
        id: u.id,
        name_f: u.name_f,
        name_l: u.name_l,
      }));
    }
  } else {
    // Fetch existing employees
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
  }

  // Update order.updated_at
  await supabase
    .from("orders")
    .update({ updated_at: new Date().toISOString() })
    .eq("id", updatedTask.order_id);

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
