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

interface CreateOrderBody {
  user_id: string;
  service_id?: string | null;
  service?: string;
  status?: number;
  employees?: string[];
  tags?: string[];
  note?: string | null;
  number?: string;
  metadata?: MetadataItem[];
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

function generateOrderNumber(): string {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  let result = "";
  for (let i = 0; i < 8; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
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

export async function createOrder(request: NextRequest, orgId: string) {
  let body: CreateOrderBody;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ message: "Invalid JSON body" }, { status: 400 });
  }

  const errors: Record<string, string[]> = {};

  // Required: user_id
  if (!body.user_id) {
    errors.user_id = ["The user_id field is required."];
  } else if (!isValidUUID(body.user_id)) {
    errors.user_id = ["The user_id must be a valid UUID."];
  }

  // Required: service_id OR service
  if (!body.service_id && !body.service) {
    errors.service = ["Either service_id or service must be provided."];
  }

  // Validate status
  if (body.status !== undefined && ![0, 1, 2, 3, 4].includes(body.status)) {
    errors.status = ["The status must be 0, 1, 2, 3, or 4."];
  }

  if (Object.keys(errors).length > 0) {
    return NextResponse.json({ message: "The given data was invalid.", errors }, { status: 400 });
  }

  // Validate user_id exists (client)
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

  // Snapshot fields from service
  let serviceName = body.service || "Custom Order";
  let price = "0.00";
  let currency = "USD";

  if (body.service_id) {
    if (!isValidUUID(body.service_id)) {
      return NextResponse.json({
        message: "The given data was invalid.",
        errors: { service_id: ["The specified service does not exist."] },
      }, { status: 422 });
    }

    const { data: service } = await supabase
      .from("services")
      .select("id, name, price, currency")
      .eq("id", body.service_id)
      .is("deleted_at", null)
      .single();

    if (!service) {
      return NextResponse.json({
        message: "The given data was invalid.",
        errors: { service_id: ["The specified service does not exist."] },
      }, { status: 422 });
    }

    serviceName = body.service || service.name;
    price = service.price || "0.00";
    currency = service.currency || "USD";
  }

  // Validate employees
  if (body.employees && body.employees.length > 0) {
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

  // Check unique number if provided
  const orderNumber = body.number || generateOrderNumber();
  if (body.number) {
    const { data: existing } = await supabase
      .from("orders")
      .select("id")
      .eq("number", body.number)
      .single();

    if (existing) {
      return NextResponse.json({
        message: "The given data was invalid.",
        errors: { number: ["The order number has already been taken."] },
      }, { status: 400 });
    }
  }

  const metadataObj = transformMetadata(body.metadata);

  // Create order
  const { data: newOrder, error: orderError } = await supabase
    .from("orders")
    .insert({
      org_id: orgId,
      number: orderNumber,
      user_id: body.user_id,
      service_id: body.service_id || null,
      service_name: serviceName,
      price: price,
      currency: currency,
      quantity: 1,
      status: body.status ?? 0,
      note: body.note ?? null,
      form_data: {},
      metadata: metadataObj,
      created_at: body.created_at || new Date().toISOString(),
      date_started: body.date_started ?? null,
      date_completed: body.date_completed ?? null,
      date_due: body.date_due ?? null,
    })
    .select()
    .single();

  if (orderError || !newOrder) {
    console.error("Order creation error:", orderError);
    return NextResponse.json({ error: "Failed to create order" }, { status: 500 });
  }

  // Assign employees
  if (body.employees && body.employees.length > 0) {
    const employeeRows = body.employees.map((empId) => ({
      order_id: newOrder.id,
      employee_id: empId,
    }));

    await supabase.from("order_employees").insert(employeeRows);
  }

  // Assign tags
  if (body.tags && body.tags.length > 0) {
    for (const tagName of body.tags) {
      // Find or create tag
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
          order_id: newOrder.id,
          tag_id: tag.id,
        });
      }
    }
  }

  // Fetch full response
  const [clientObj, employees, tags] = await Promise.all([
    fetchClient(body.user_id),
    fetchOrderEmployees(newOrder.id),
    fetchOrderTags(newOrder.id),
  ]);

  const response = {
    id: newOrder.id,
    number: newOrder.number,
    created_at: newOrder.created_at,
    updated_at: newOrder.updated_at,
    last_message_at: newOrder.last_message_at,
    date_started: newOrder.date_started,
    date_completed: newOrder.date_completed,
    date_due: newOrder.date_due,
    client: clientObj,
    tags,
    status: STATUS_MAP[newOrder.status] || "Unknown",
    price: newOrder.price,
    quantity: newOrder.quantity,
    invoice_id: newOrder.invoice_id,
    service: newOrder.service_name,
    service_id: newOrder.service_id,
    user_id: newOrder.user_id,
    employees,
    note: newOrder.note,
    form_data: newOrder.form_data || {},
    paysys: newOrder.paysys,
  };

  return NextResponse.json(response, { status: 201 });
}
