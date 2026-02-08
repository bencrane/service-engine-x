import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

const STATUS_MAP: Record<number, string> = {
  0: "Unpaid",
  1: "In Progress",
  2: "Completed",
  3: "Cancelled",
  4: "On Hold",
};

interface OrderRow {
  id: string;
  number: string;
  user_id: string;
  service_id: string | null;
  service_name: string;
  price: string;
  currency: string;
  quantity: number;
  status: number;
  invoice_id: string | null;
  note: string | null;
  form_data: Record<string, unknown>;
  paysys: string | null;
  date_started: string | null;
  date_completed: string | null;
  date_due: string | null;
  last_message_at: string | null;
  created_at: string;
  updated_at: string;
}

function isValidUUID(str: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

async function fetchClient(userId: string) {
  const { data: user } = await supabase
    .from("users")
    .select(`
      id,
      name_f,
      name_l,
      email,
      company,
      phone,
      address_id,
      role_id,
      addresses (
        id, line_1, line_2, city, state, postcode, country
      ),
      roles (
        id, name
      )
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

async function serializeIndexOrder(order: OrderRow) {
  const [client, employees, tags] = await Promise.all([
    fetchClient(order.user_id),
    fetchOrderEmployees(order.id),
    fetchOrderTags(order.id),
  ]);

  return {
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
  };
}

export async function listOrders(request: NextRequest, orgId: string) {
  const { searchParams } = new URL(request.url);

  const limit = Math.min(Math.max(parseInt(searchParams.get("limit") || "20", 10), 1), 100);
  const page = Math.max(parseInt(searchParams.get("page") || "1", 10), 1);
  const offset = (page - 1) * limit;

  const sortParam = searchParams.get("sort") || "created_at:desc";
  const [sortField, sortDirection] = sortParam.split(":");
  const validSortFields = ["id", "number", "status", "price", "quantity", "user_id", "service_id", "created_at", "date_due"];
  const actualSortField = validSortFields.includes(sortField) ? sortField : "created_at";
  const ascending = sortDirection === "asc";

  // Build count query
  let countQuery = supabase
    .from("orders")
    .select("*", { count: "exact", head: true })
    .eq("org_id", orgId)
    .is("deleted_at", null);

  // Build data query
  let query = supabase
    .from("orders")
    .select("*")
    .eq("org_id", orgId)
    .is("deleted_at", null);

  const filterableFields = ["id", "number", "status", "user_id", "service_id", "price", "invoice_id", "created_at", "date_due"];

  // Apply filters to both queries
  for (const [key, value] of searchParams.entries()) {
    const filterMatch = key.match(/^filters\[(\w+)\]\[(\$\w+)\](\[\])?$/);
    if (filterMatch) {
      const [, field, operator] = filterMatch;
      if (!filterableFields.includes(field)) continue;

      switch (operator) {
        case "$eq":
          if (value === "null") {
            countQuery = countQuery.is(field, null);
            query = query.is(field, null);
          } else {
            countQuery = countQuery.eq(field, value);
            query = query.eq(field, value);
          }
          break;
        case "$lt":
          countQuery = countQuery.lt(field, value);
          query = query.lt(field, value);
          break;
        case "$gt":
          countQuery = countQuery.gt(field, value);
          query = query.gt(field, value);
          break;
        case "$in":
          const inValues = searchParams.getAll(`filters[${field}][$in][]`);
          if (inValues.length > 0) {
            countQuery = countQuery.in(field, inValues);
            query = query.in(field, inValues);
          }
          break;
      }
    }
  }

  const { count: total } = await countQuery;

  query = query.order(actualSortField, { ascending });
  query = query.range(offset, offset + limit - 1);

  const { data: orders, error } = await query;

  if (error) {
    return NextResponse.json({ error: "Database error" }, { status: 500 });
  }

  const totalCount = total || 0;
  const lastPage = Math.ceil(totalCount / limit) || 1;
  const baseUrl = request.url.split("?")[0];

  const serializedOrders = await Promise.all(
    (orders as OrderRow[]).map(serializeIndexOrder)
  );

  const response = {
    data: serializedOrders,
    links: {
      first: `${baseUrl}?page=1&limit=${limit}`,
      last: `${baseUrl}?page=${lastPage}&limit=${limit}`,
      prev: page > 1 ? `${baseUrl}?page=${page - 1}&limit=${limit}` : null,
      next: page < lastPage ? `${baseUrl}?page=${page + 1}&limit=${limit}` : null,
    },
    meta: {
      current_page: page,
      from: totalCount > 0 ? offset + 1 : 0,
      to: Math.min(offset + limit, totalCount),
      last_page: lastPage,
      per_page: limit,
      total: totalCount,
      path: baseUrl,
      links: buildPaginationLinks(page, lastPage, baseUrl, limit),
    },
  };

  return NextResponse.json(response);
}

function buildPaginationLinks(currentPage: number, lastPage: number, baseUrl: string, limit: number) {
  const links: { url: string | null; label: string; active: boolean }[] = [];

  links.push({
    url: currentPage > 1 ? `${baseUrl}?page=${currentPage - 1}&limit=${limit}` : null,
    label: "Previous",
    active: false,
  });

  for (let i = 1; i <= Math.min(lastPage, 10); i++) {
    links.push({
      url: `${baseUrl}?page=${i}&limit=${limit}`,
      label: String(i),
      active: i === currentPage,
    });
  }

  links.push({
    url: currentPage < lastPage ? `${baseUrl}?page=${currentPage + 1}&limit=${limit}` : null,
    label: "Next",
    active: false,
  });

  return links;
}
