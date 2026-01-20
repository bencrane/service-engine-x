import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

interface ClientRow {
  id: string;
  email: string;
  name_f: string;
  name_l: string;
  company: string | null;
  phone: string | null;
  tax_id: string | null;
  note: string | null;
  role_id: string;
  status: number;
  balance: string;
  spent: string;
  optin: string | null;
  stripe_id: string | null;
  custom_fields: Record<string, unknown>;
  aff_id: number | null;
  aff_link: string | null;
  ga_cid: string | null;
  address_id: string | null;
  created_at: string;
  updated_at: string;
  address: AddressRow | null;
  role: RoleRow;
}

interface AddressRow {
  id: string;
  line_1: string | null;
  line_2: string | null;
  city: string | null;
  state: string | null;
  country: string | null;
  postcode: string | null;
  name_f: string | null;
  name_l: string | null;
  tax_id: string | null;
  company_name: string | null;
  company_vat: string | null;
}

interface RoleRow {
  id: string;
  name: string;
  dashboard_access: number;
  order_access: number;
  order_management: number;
  ticket_access: number;
  ticket_management: number;
  invoice_access: number;
  invoice_management: number;
  clients: number;
  services: number;
  coupons: number;
  forms: number;
  messaging: number;
  affiliates: number;
  settings_company: boolean;
  settings_payments: boolean;
  settings_team: boolean;
  settings_modules: boolean;
  settings_integrations: boolean;
  settings_orders: boolean;
  settings_tickets: boolean;
  settings_accounts: boolean;
  settings_messages: boolean;
  settings_tags: boolean;
  settings_sidebar: boolean;
  settings_dashboard: boolean;
  settings_templates: boolean;
  settings_emails: boolean;
  settings_language: boolean;
  settings_logs: boolean;
  created_at: string;
  updated_at: string;
}

function serializeAddress(address: AddressRow | null) {
  if (!address) return null;
  return {
    line_1: address.line_1,
    line_2: address.line_2,
    city: address.city,
    state: address.state,
    country: address.country,
    postcode: address.postcode,
    name_f: address.name_f,
    name_l: address.name_l,
    tax_id: address.tax_id,
    company_name: address.company_name,
    company_vat: address.company_vat,
  };
}

function serializeRole(role: RoleRow) {
  return {
    id: role.id,
    name: role.name,
    dashboard_access: role.dashboard_access,
    order_access: role.order_access,
    order_management: role.order_management,
    ticket_access: role.ticket_access,
    ticket_management: role.ticket_management,
    invoice_access: role.invoice_access,
    invoice_management: role.invoice_management,
    clients: role.clients,
    services: role.services,
    coupons: role.coupons,
    forms: role.forms,
    messaging: role.messaging,
    affiliates: role.affiliates,
    settings_company: role.settings_company,
    settings_payments: role.settings_payments,
    settings_team: role.settings_team,
    settings_modules: role.settings_modules,
    settings_integrations: role.settings_integrations,
    settings_orders: role.settings_orders,
    settings_tickets: role.settings_tickets,
    settings_accounts: role.settings_accounts,
    settings_messages: role.settings_messages,
    settings_tags: role.settings_tags,
    settings_sidebar: role.settings_sidebar,
    settings_dashboard: role.settings_dashboard,
    settings_templates: role.settings_templates,
    settings_emails: role.settings_emails,
    settings_language: role.settings_language,
    settings_logs: role.settings_logs,
    created_at: role.created_at,
    updated_at: role.updated_at,
  };
}

function serializeClient(client: ClientRow) {
  return {
    id: client.id,
    name: `${client.name_f} ${client.name_l}`.trim(),
    name_f: client.name_f,
    name_l: client.name_l,
    email: client.email,
    company: client.company,
    phone: client.phone,
    tax_id: client.tax_id,
    address: serializeAddress(client.address),
    note: client.note,
    balance: client.balance,
    spent: client.spent,
    optin: client.optin,
    stripe_id: client.stripe_id,
    custom_fields: client.custom_fields,
    status: client.status,
    aff_id: client.aff_id,
    aff_link: client.aff_link,
    role_id: client.role_id,
    role: serializeRole(client.role),
    created_at: client.created_at,
  };
}

export async function listClients(request: NextRequest) {
  const { searchParams } = new URL(request.url);

  const limit = Math.min(Math.max(parseInt(searchParams.get("limit") || "20", 10), 1), 100);
  const page = Math.max(parseInt(searchParams.get("page") || "1", 10), 1);
  const offset = (page - 1) * limit;

  const sortParam = searchParams.get("sort") || "created_at:desc";
  const [sortField, sortDirection] = sortParam.split(":");
  const validSortFields = ["id", "email", "name_f", "name_l", "status", "balance", "created_at"];
  const actualSortField = validSortFields.includes(sortField) ? sortField : "created_at";
  const ascending = sortDirection === "asc";

  const { data: clientRole } = await supabase
    .from("roles")
    .select("id")
    .eq("dashboard_access", 0)
    .single();

  if (!clientRole) {
    return NextResponse.json({ error: "Client role not configured" }, { status: 500 });
  }

  let query = supabase
    .from("users")
    .select(`
      *,
      address:addresses(*),
      role:roles(*)
    `, { count: "exact" })
    .eq("role_id", clientRole.id);

  for (const [key, value] of searchParams.entries()) {
    const filterMatch = key.match(/^filters\[(\w+)\]\[(\$\w+)\](\[\])?$/);
    if (filterMatch) {
      const [, field, operator] = filterMatch;
      const filterableFields = ["id", "email", "status", "balance", "created_at"];
      if (!filterableFields.includes(field)) continue;

      switch (operator) {
        case "$eq":
          query = query.eq(field, value);
          break;
        case "$lt":
          query = query.lt(field, value);
          break;
        case "$gt":
          query = query.gt(field, value);
          break;
        case "$in":
          const inValues = searchParams.getAll(`filters[${field}][$in][]`);
          if (inValues.length > 0) {
            query = query.in(field, inValues);
          }
          break;
      }
    }
  }

  query = query.order(actualSortField, { ascending });

  const { count: total } = await query;

  query = query.range(offset, offset + limit - 1);

  const { data: clients, error } = await query;

  if (error) {
    return NextResponse.json({ error: "Database error" }, { status: 500 });
  }

  const totalCount = total || 0;
  const lastPage = Math.ceil(totalCount / limit) || 1;

  const baseUrl = request.url.split("?")[0];

  const response = {
    data: (clients as ClientRow[]).map(serializeClient),
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

  for (let i = 1; i <= lastPage; i++) {
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
