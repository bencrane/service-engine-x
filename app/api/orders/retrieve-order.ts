import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

const STATUS_MAP: Record<number, string> = {
  0: "Unpaid",
  1: "In Progress",
  2: "Completed",
  3: "Cancelled",
  4: "On Hold",
};

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

async function fetchOrderMessages(orderId: string) {
  const { data: messages } = await supabase
    .from("order_messages")
    .select("id, user_id, message, staff_only, files, created_at")
    .eq("order_id", orderId)
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

async function fetchService(serviceId: string | null) {
  if (!serviceId) return null;

  const { data: service } = await supabase
    .from("services")
    .select("*")
    .eq("id", serviceId)
    .is("deleted_at", null)
    .single();

  return service || null;
}

async function fetchInvoice(invoiceId: string | null) {
  if (!invoiceId) return null;

  const { data: invoice } = await supabase
    .from("invoices")
    .select(`
      *,
      invoice_items (*)
    `)
    .eq("id", invoiceId)
    .is("deleted_at", null)
    .single();

  return invoice || null;
}

async function fetchSubscription(subscriptionId: string | null) {
  if (!subscriptionId) return null;

  const { data: subscription } = await supabase
    .from("subscriptions")
    .select("*")
    .eq("id", subscriptionId)
    .single();

  return subscription || null;
}

export async function retrieveOrder(id: string, orgId: string) {
  if (!isValidUUID(id)) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  const { data: order, error } = await supabase
    .from("orders")
    .select("*")
    .eq("id", id)
    .eq("org_id", orgId)
    .is("deleted_at", null)
    .single();

  if (error || !order) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  const [client, employees, tags, messages, orderService, invoice, subscription] = await Promise.all([
    fetchClient(order.user_id),
    fetchOrderEmployees(order.id),
    fetchOrderTags(order.id),
    fetchOrderMessages(order.id),
    fetchService(order.service_id),
    fetchInvoice(order.invoice_id),
    fetchSubscription(order.subscription_id),
  ]);

  const response = {
    id: order.id,
    number: order.number,
    created_at: order.created_at,
    updated_at: order.updated_at,
    last_message_at: order.last_message_at,
    date_started: order.date_started,
    date_completed: order.date_completed,
    date_due: order.date_due,
    client,
    tags,
    status: STATUS_MAP[order.status] || "Unknown",
    price: order.price,
    quantity: order.quantity,
    invoice_id: order.invoice_id,
    service: order.service_name,
    service_id: order.service_id,
    user_id: order.user_id,
    employees,
    note: order.note,
    form_data: order.form_data || {},
    paysys: order.paysys,
    currency: order.currency,
    metadata: order.metadata || {},
    subscription,
    invoice,
    order_service: orderService,
    messages,
    options: {},
  };

  return NextResponse.json(response);
}
