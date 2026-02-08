import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

const STATUS_MAP: Record<number, string> = {
  0: "Unpaid",
  1: "In Progress",
  2: "Completed",
  3: "Cancelled",
  4: "On Hold",
};

interface MetadataItem {
  title: string;
  value: string;
}

interface UpdateOrderBody {
  status?: number;
  employees?: string[];
  tags?: string[];
  note?: string | null;
  service_id?: string | null;
  form_data?: Record<string, unknown>;
  metadata?: MetadataItem[] | null;
  created_at?: string;
  date_started?: string | null;
  date_completed?: string | null;
  date_due?: string | null;
}

function isValidUUID(str: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

function transformMetadata(metadata: MetadataItem[] | null | undefined): Record<string, string> {
  if (!metadata || !Array.isArray(metadata)) return {};
  const result: Record<string, string> = {};
  for (const item of metadata) {
    if (item.title && typeof item.title === "string") {
      result[item.title] = String(item.value ?? "");
    }
  }
  return result;
}

async function fetchClient(userId: string) {
  const { data: user } = await supabase
    .from("users")
    .select(`
      id, name_f, name_l, email, company, phone, address_id, role_id,
      addresses (id, line_1, line_2, city, state, postcode, country),
      roles (id, name)
    `)
    .eq("id", userId)
    .single();

  if (!user) return null;

  const addressArray = user.addresses as Record<string, unknown>[] | null;
  const address = Array.isArray(addressArray) ? addressArray[0] || null : null;
  const roleArray = user.roles as Record<string, unknown>[] | null;
  const role = Array.isArray(roleArray) ? roleArray[0] || null : null;

  return {
    id: user.id,
    name: `${user.name_f} ${user.name_l}`.trim(),
    name_f: user.name_f,
    name_l: user.name_l,
    email: user.email,
    company: user.company,
    phone: user.phone,
    address: address || null,
    role: role || null,
  };
}

async function fetchOrderEmployees(orderId: string) {
  const { data: assignments } = await supabase
    .from("order_employees")
    .select("employee_id")
    .eq("order_id", orderId);

  if (!assignments || assignments.length === 0) return [];

  const employeeIds = assignments.map((a) => a.employee_id);
  const { data: employees } = await supabase
    .from("users")
    .select("id, name_f, name_l, role_id")
    .in("id", employeeIds);

  return (employees || []).map((emp) => ({
    id: emp.id,
    name_f: emp.name_f,
    name_l: emp.name_l,
    role_id: emp.role_id,
  }));
}

async function fetchOrderTags(orderId: string) {
  const { data: tagLinks } = await supabase
    .from("order_tags")
    .select("tag_id")
    .eq("order_id", orderId);

  if (!tagLinks || tagLinks.length === 0) return [];

  const tagIds = tagLinks.map((t) => t.tag_id);
  const { data: tags } = await supabase
    .from("tags")
    .select("name")
    .in("id", tagIds);

  return (tags || []).map((t) => t.name);
}

export async function updateOrder(request: NextRequest, id: string, orgId: string) {
  if (!isValidUUID(id)) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  let body: UpdateOrderBody;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ message: "Invalid JSON body" }, { status: 400 });
  }

  // Check order exists
  const { data: existingOrder, error: fetchError } = await supabase
    .from("orders")
    .select("*")
    .eq("id", id)
    .eq("org_id", orgId)
    .is("deleted_at", null)
    .single();

  if (fetchError || !existingOrder) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  const errors: Record<string, string[]> = {};

  // Validate status
  if (body.status !== undefined && ![0, 1, 2, 3, 4].includes(body.status)) {
    errors.status = ["The status must be between 0 and 4."];
  }

  if (Object.keys(errors).length > 0) {
    return NextResponse.json({ message: "The given data was invalid.", errors }, { status: 400 });
  }

  // Validate service_id if provided
  if (body.service_id !== undefined && body.service_id !== null) {
    if (!isValidUUID(body.service_id)) {
      return NextResponse.json({
        message: "The given data was invalid.",
        errors: { service_id: ["The specified service does not exist."] },
      }, { status: 422 });
    }

    const { data: service } = await supabase
      .from("services")
      .select("id")
      .eq("id", body.service_id)
      .is("deleted_at", null)
      .single();

    if (!service) {
      return NextResponse.json({
        message: "The given data was invalid.",
        errors: { service_id: ["The specified service does not exist."] },
      }, { status: 422 });
    }
  }

  // Validate employees
  if (body.employees !== undefined) {
    for (const empId of body.employees) {
      if (!isValidUUID(empId)) {
        return NextResponse.json({
          message: "The given data was invalid.",
          errors: { employees: [`Employee with ID ${empId} does not exist.`] },
        }, { status: 422 });
      }

      const { data: emp } = await supabase
        .from("users")
        .select("id, role:roles(dashboard_access)")
        .eq("id", empId)
        .single();

      const role = emp?.role as { dashboard_access: number } | { dashboard_access: number }[] | null;
      const dashboardAccess = Array.isArray(role) ? role[0]?.dashboard_access : role?.dashboard_access;
      
      if (!emp || !role || dashboardAccess === 0) {
        return NextResponse.json({
          message: "The given data was invalid.",
          errors: { employees: [`Employee with ID ${empId} does not exist.`] },
        }, { status: 422 });
      }
    }
  }

  // Build update payload
  const updatePayload: Record<string, unknown> = {
    updated_at: new Date().toISOString(),
  };

  if (body.status !== undefined) updatePayload.status = body.status;
  if (body.note !== undefined) updatePayload.note = body.note;
  if (body.service_id !== undefined) updatePayload.service_id = body.service_id;
  if (body.form_data !== undefined) updatePayload.form_data = body.form_data;
  if (body.created_at !== undefined) updatePayload.created_at = body.created_at;
  if (body.date_started !== undefined) updatePayload.date_started = body.date_started;
  if (body.date_completed !== undefined) updatePayload.date_completed = body.date_completed;
  if (body.date_due !== undefined) updatePayload.date_due = body.date_due;

  if (body.metadata !== undefined) {
    if (body.metadata === null || (Array.isArray(body.metadata) && body.metadata.length === 0)) {
      updatePayload.metadata = {};
    } else {
      updatePayload.metadata = transformMetadata(body.metadata);
    }
  }

  // Update order
  const { data: updatedOrder, error: updateError } = await supabase
    .from("orders")
    .update(updatePayload)
    .eq("id", id)
    .select()
    .single();

  if (updateError || !updatedOrder) {
    return NextResponse.json({ error: "Failed to update order" }, { status: 500 });
  }

  // Replace employees if provided
  if (body.employees !== undefined) {
    await supabase.from("order_employees").delete().eq("order_id", id);

    if (body.employees.length > 0) {
      const employeeRows = body.employees.map((empId) => ({
        order_id: id,
        employee_id: empId,
      }));
      await supabase.from("order_employees").insert(employeeRows);
    }
  }

  // Replace tags if provided
  if (body.tags !== undefined) {
    await supabase.from("order_tags").delete().eq("order_id", id);

    for (const tagName of body.tags) {
      let { data: tag } = await supabase
        .from("tags")
        .select("id")
        .eq("name", tagName)
        .single();

      if (!tag) {
        const { data: newTag } = await supabase
          .from("tags")
          .insert({ name: tagName })
          .select("id")
          .single();
        tag = newTag;
      }

      if (tag) {
        await supabase.from("order_tags").insert({
          order_id: id,
          tag_id: tag.id,
        });
      }
    }
  }

  // Fetch full response
  const [client, employees, tags] = await Promise.all([
    fetchClient(updatedOrder.user_id),
    fetchOrderEmployees(id),
    fetchOrderTags(id),
  ]);

  const response = {
    id: updatedOrder.id,
    number: updatedOrder.number,
    created_at: updatedOrder.created_at,
    updated_at: updatedOrder.updated_at,
    last_message_at: updatedOrder.last_message_at,
    date_started: updatedOrder.date_started,
    date_completed: updatedOrder.date_completed,
    date_due: updatedOrder.date_due,
    client,
    tags,
    status: STATUS_MAP[updatedOrder.status] || "Unknown",
    price: updatedOrder.price,
    quantity: updatedOrder.quantity,
    invoice_id: updatedOrder.invoice_id,
    service: updatedOrder.service_name,
    service_id: updatedOrder.service_id,
    user_id: updatedOrder.user_id,
    employees,
    note: updatedOrder.note,
    form_data: updatedOrder.form_data || {},
    paysys: updatedOrder.paysys,
  };

  return NextResponse.json(response);
}
