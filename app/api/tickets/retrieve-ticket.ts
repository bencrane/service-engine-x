import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

const TICKET_STATUS_MAP: Record<number, string> = {
  1: "Open",
  2: "Pending",
  3: "Closed",
};

function isValidUUID(str: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

async function fetchClient(userId: string) {
  const { data: user } = await supabase
    .from("users")
    .select(`
      id, name_f, name_l, email, company, phone, address_id, role_id, balance,
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
    balance: user.balance,
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

async function fetchTicketMessages(ticketId: string) {
  const { data: messages } = await supabase
    .from("ticket_messages")
    .select("id, user_id, message, staff_only, files, created_at")
    .eq("ticket_id", ticketId)
    .order("created_at", { ascending: true });

  return (messages || []).map((msg) => ({
    id: msg.id,
    user_id: msg.user_id,
    message: msg.message,
    staff_only: msg.staff_only,
    files: msg.files || [],
    created_at: msg.created_at,
  }));
}

async function fetchOrder(orderId: string | null) {
  if (!orderId) return null;

  const { data: order } = await supabase
    .from("orders")
    .select("id, status, service_name, price, quantity, created_at")
    .eq("id", orderId)
    .is("deleted_at", null)
    .single();

  if (!order) return null;

  const STATUS_MAP: Record<number, string> = {
    0: "Unpaid",
    1: "In Progress",
    2: "Completed",
    3: "Cancelled",
    4: "On Hold",
  };

  return {
    id: order.id,
    status: STATUS_MAP[order.status] || "Unknown",
    service: order.service_name,
    price: parseFloat(order.price),
    quantity: order.quantity,
    created_at: order.created_at,
  };
}

export async function retrieveTicket(id: string) {
  if (!isValidUUID(id)) {
    return NextResponse.json({ error: "Invalid ticket ID format." }, { status: 400 });
  }

  const { data: ticket, error } = await supabase
    .from("tickets")
    .select("*")
    .eq("id", id)
    .is("deleted_at", null)
    .single();

  if (error || !ticket) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  const [client, employees, tags, messages, order] = await Promise.all([
    fetchClient(ticket.user_id),
    fetchTicketEmployees(ticket.id),
    fetchTicketTags(ticket.id),
    fetchTicketMessages(ticket.id),
    fetchOrder(ticket.order_id),
  ]);

  const response = {
    id: ticket.id,
    subject: ticket.subject,
    user_id: ticket.user_id,
    order_id: ticket.order_id,
    status: TICKET_STATUS_MAP[ticket.status] || "Unknown",
    status_id: ticket.status,
    source: ticket.source,
    note: ticket.note,
    form_data: ticket.form_data || {},
    metadata: ticket.metadata || {},
    tags,
    employees,
    client,
    order,
    messages,
    created_at: ticket.created_at,
    updated_at: ticket.updated_at,
    last_message_at: ticket.last_message_at,
    date_closed: ticket.date_closed,
  };

  return NextResponse.json(response);
}
