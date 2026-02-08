import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

const TICKET_STATUS_MAP: Record<number, string> = {
  1: "Open",
  2: "Pending",
  3: "Closed",
};

interface UpdateTicketBody {
  subject?: string;
  status?: number;
  order_id?: string | null;
  employees?: string[];
  tags?: string[];
  note?: string | null;
  metadata?: Record<string, unknown>;
}

function isValidUUID(str: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
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

  const address = user.addresses as Record<string, unknown> | null;
  const role = user.roles as Record<string, unknown> | null;

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

async function fetchTicketEmployees(ticketId: string) {
  const { data: assignments } = await supabase
    .from("ticket_employees")
    .select("employee_id")
    .eq("ticket_id", ticketId);

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

async function fetchTicketTags(ticketId: string) {
  const { data: tagLinks } = await supabase
    .from("ticket_tags")
    .select("tag_id")
    .eq("ticket_id", ticketId);

  if (!tagLinks || tagLinks.length === 0) return [];

  const tagIds = tagLinks.map((t) => t.tag_id);
  const { data: tags } = await supabase
    .from("tags")
    .select("name")
    .in("id", tagIds);

  return (tags || []).map((t) => t.name);
}

export async function updateTicket(request: NextRequest, id: string) {
  if (!isValidUUID(id)) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  let body: UpdateTicketBody;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ message: "Invalid JSON body" }, { status: 400 });
  }

  // Check ticket exists
  const { data: existingTicket, error: fetchError } = await supabase
    .from("tickets")
    .select("*")
    .eq("id", id)
    .is("deleted_at", null)
    .single();

  if (fetchError || !existingTicket) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  const errors: Record<string, string[]> = {};

  // Validate status
  if (body.status !== undefined && ![1, 2, 3].includes(body.status)) {
    errors.status = ["The selected status is invalid."];
  }

  // Validate subject
  if (body.subject !== undefined) {
    if (typeof body.subject !== "string" || body.subject.trim() === "") {
      errors.subject = ["The subject must be a non-empty string."];
    }
  }

  if (Object.keys(errors).length > 0) {
    return NextResponse.json({ message: "The given data was invalid.", errors }, { status: 400 });
  }

  // Validate order_id if provided
  if (body.order_id !== undefined && body.order_id !== null) {
    if (!isValidUUID(body.order_id)) {
      return NextResponse.json({
        message: "The given data was invalid.",
        errors: { order_id: ["The specified order does not exist."] },
      }, { status: 422 });
    }

    const { data: order } = await supabase
      .from("orders")
      .select("id")
      .eq("id", body.order_id)
      .is("deleted_at", null)
      .single();

    if (!order) {
      return NextResponse.json({
        message: "The given data was invalid.",
        errors: { order_id: ["The specified order does not exist."] },
      }, { status: 422 });
    }
  }

  // Validate employees
  if (body.employees !== undefined) {
    for (const empId of body.employees) {
      if (!isValidUUID(empId)) {
        return NextResponse.json({
          message: "The given data was invalid.",
          errors: { employees: [`The specified employee does not exist.`] },
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
          errors: { employees: [`The specified employee does not exist.`] },
        }, { status: 422 });
      }
    }
  }

  // Build update payload
  const updatePayload: Record<string, unknown> = {
    updated_at: new Date().toISOString(),
  };

  if (body.subject !== undefined) updatePayload.subject = body.subject.trim();
  if (body.note !== undefined) updatePayload.note = body.note;
  if (body.order_id !== undefined) updatePayload.order_id = body.order_id;
  if (body.metadata !== undefined) updatePayload.metadata = body.metadata ?? {};

  // Handle status change
  if (body.status !== undefined) {
    updatePayload.status = body.status;
    
    // Set date_closed when status changes to Closed (3)
    if (body.status === 3 && existingTicket.status !== 3) {
      updatePayload.date_closed = new Date().toISOString();
    }
    // Clear date_closed when status changes from Closed to other
    if (body.status !== 3 && existingTicket.status === 3) {
      updatePayload.date_closed = null;
    }
  }

  // Update ticket
  const { data: updatedTicket, error: updateError } = await supabase
    .from("tickets")
    .update(updatePayload)
    .eq("id", id)
    .select()
    .single();

  if (updateError || !updatedTicket) {
    return NextResponse.json({ error: "Failed to update ticket" }, { status: 500 });
  }

  // Replace employees if provided
  if (body.employees !== undefined) {
    await supabase.from("ticket_employees").delete().eq("ticket_id", id);

    if (body.employees.length > 0) {
      const employeeRows = body.employees.map((empId) => ({
        ticket_id: id,
        employee_id: empId,
      }));
      await supabase.from("ticket_employees").insert(employeeRows);
    }
  }

  // Replace tags if provided
  if (body.tags !== undefined) {
    await supabase.from("ticket_tags").delete().eq("ticket_id", id);

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
        await supabase.from("ticket_tags").insert({
          ticket_id: id,
          tag_id: tag.id,
        });
      }
    }
  }

  // Fetch full response
  const [client, employees, tags] = await Promise.all([
    fetchClient(updatedTicket.user_id),
    fetchTicketEmployees(id),
    fetchTicketTags(id),
  ]);

  const response = {
    id: updatedTicket.id,
    subject: updatedTicket.subject,
    user_id: updatedTicket.user_id,
    order_id: updatedTicket.order_id,
    status: TICKET_STATUS_MAP[updatedTicket.status] || "Unknown",
    status_id: updatedTicket.status,
    source: updatedTicket.source,
    note: updatedTicket.note,
    form_data: updatedTicket.form_data || {},
    metadata: updatedTicket.metadata || {},
    tags,
    employees,
    client,
    created_at: updatedTicket.created_at,
    updated_at: updatedTicket.updated_at,
    last_message_at: updatedTicket.last_message_at,
    date_closed: updatedTicket.date_closed,
  };

  return NextResponse.json(response);
}
