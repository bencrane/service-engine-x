import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

const TICKET_STATUS_MAP: Record<number, string> = {
  1: "Open",
  2: "Pending",
  3: "Closed",
};

interface CreateTicketBody {
  user_id: string;
  subject: string;
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

export async function createTicket(request: NextRequest) {
  let body: CreateTicketBody;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ message: "Invalid JSON body" }, { status: 400 });
  }

  const errors: Record<string, string[]> = {};

  // Required fields
  if (!body.user_id) {
    errors.user_id = ["The user_id field is required."];
  } else if (!isValidUUID(body.user_id)) {
    errors.user_id = ["The user_id must be a valid UUID."];
  }

  if (!body.subject || typeof body.subject !== "string" || body.subject.trim() === "") {
    errors.subject = ["The subject field is required."];
  }

  // Validate status
  if (body.status !== undefined && ![1, 2, 3].includes(body.status)) {
    errors.status = ["The selected status is invalid."];
  }

  if (Object.keys(errors).length > 0) {
    return NextResponse.json({ message: "The given data was invalid.", errors }, { status: 400 });
  }

  // Validate client exists
  const { data: client } = await supabase
    .from("users")
    .select("id")
    .eq("id", body.user_id)
    .single();

  if (!client) {
    return NextResponse.json({
      message: "The given data was invalid.",
      errors: { user_id: ["The specified client does not exist."] },
    }, { status: 422 });
  }

  // Validate order_id if provided
  if (body.order_id) {
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
  if (body.employees && body.employees.length > 0) {
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

  // Create ticket
  const { data: newTicket, error: ticketError } = await supabase
    .from("tickets")
    .insert({
      user_id: body.user_id,
      subject: body.subject.trim(),
      status: body.status ?? 1, // Default: Open
      order_id: body.order_id || null,
      note: body.note ?? null,
      metadata: body.metadata ?? {},
      form_data: {},
      source: "API",
    })
    .select()
    .single();

  if (ticketError || !newTicket) {
    console.error("Ticket creation error:", ticketError);
    return NextResponse.json({ error: "Failed to create ticket" }, { status: 500 });
  }

  // Assign employees
  if (body.employees && body.employees.length > 0) {
    const employeeRows = body.employees.map((empId) => ({
      ticket_id: newTicket.id,
      employee_id: empId,
    }));
    await supabase.from("ticket_employees").insert(employeeRows);
  }

  // Assign tags
  if (body.tags && body.tags.length > 0) {
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
          ticket_id: newTicket.id,
          tag_id: tag.id,
        });
      }
    }
  }

  // Fetch full response
  const [clientObj, employees, tags] = await Promise.all([
    fetchClient(body.user_id),
    fetchTicketEmployees(newTicket.id),
    fetchTicketTags(newTicket.id),
  ]);

  const response = {
    id: newTicket.id,
    subject: newTicket.subject,
    user_id: newTicket.user_id,
    order_id: newTicket.order_id,
    status: TICKET_STATUS_MAP[newTicket.status] || "Unknown",
    status_id: newTicket.status,
    source: newTicket.source,
    note: newTicket.note,
    form_data: newTicket.form_data || {},
    metadata: newTicket.metadata || {},
    tags,
    employees,
    client: clientObj,
    created_at: newTicket.created_at,
    updated_at: newTicket.updated_at,
    last_message_at: newTicket.last_message_at,
    date_closed: newTicket.date_closed,
  };

  return NextResponse.json(response, { status: 201 });
}
