import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

const TICKET_STATUS_MAP: Record<number, string> = {
  1: "Open",
  2: "Pending",
  3: "Closed",
};

interface TicketRow {
  id: string;
  user_id: string;
  order_id: string | null;
  subject: string;
  status: number;
  source: string;
  note: string | null;
  form_data: Record<string, unknown>;
  metadata: Record<string, unknown>;
  last_message_at: string | null;
  date_closed: string | null;
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

async function serializeTicket(ticket: TicketRow) {
  const [client, employees, tags] = await Promise.all([
    fetchClient(ticket.user_id),
    fetchTicketEmployees(ticket.id),
    fetchTicketTags(ticket.id),
  ]);

  return {
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
    created_at: ticket.created_at,
    updated_at: ticket.updated_at,
    last_message_at: ticket.last_message_at,
    date_closed: ticket.date_closed,
  };
}

export async function listTickets(request: NextRequest) {
  const { searchParams } = new URL(request.url);

  const limit = Math.min(Math.max(parseInt(searchParams.get("limit") || "20", 10), 1), 100);
  const page = Math.max(parseInt(searchParams.get("page") || "1", 10), 1);
  const offset = (page - 1) * limit;

  const sortParam = searchParams.get("sort") || "created_at:desc";
  const [sortField, sortDirection] = sortParam.split(":");
  const validSortFields = ["id", "subject", "status", "user_id", "order_id", "created_at", "last_message_at"];
  const actualSortField = validSortFields.includes(sortField) ? sortField : "created_at";
  const ascending = sortDirection === "asc";

  // Build count query
  let countQuery = supabase
    .from("tickets")
    .select("*", { count: "exact", head: true })
    .is("deleted_at", null);

  // Build data query
  let query = supabase
    .from("tickets")
    .select("*")
    .is("deleted_at", null);

  const filterableFields = ["user_id", "status", "order_id", "created_at", "last_message_at"];

  // Apply filters
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

  const { data: tickets, error } = await query;

  if (error) {
    return NextResponse.json({ error: "Database error" }, { status: 500 });
  }

  const totalCount = total || 0;
  const lastPage = Math.ceil(totalCount / limit) || 1;
  const baseUrl = request.url.split("?")[0];

  const serializedTickets = await Promise.all(
    (tickets as TicketRow[]).map(serializeTicket)
  );

  const response = {
    data: serializedTickets,
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
    },
  };

  return NextResponse.json(response);
}
