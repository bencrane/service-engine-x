import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

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

function isValidUUID(str: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

export async function retrieveClient(id: string, orgId: string) {
  if (!isValidUUID(id)) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  const { data: clientRole } = await supabase
    .from("roles")
    .select("id")
    .eq("dashboard_access", 0)
    .single();

  if (!clientRole) {
    return NextResponse.json({ error: "Client role not configured" }, { status: 500 });
  }

  const { data: client, error } = await supabase
    .from("users")
    .select(`
      *,
      address:addresses(*),
      role:roles(*)
    `)
    .eq("id", id)
    .eq("org_id", orgId)
    .eq("role_id", clientRole.id)
    .single();

  if (error || !client) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  const clientRow = client as ClientRow;

  const { data: spentData } = await supabase
    .from("invoices")
    .select("total")
    .eq("user_id", id)
    .not("date_paid", "is", null);

  const spent = spentData && spentData.length > 0
    ? spentData.reduce((sum, inv) => sum + parseFloat(inv.total || "0"), 0).toFixed(2)
    : null;

  const response = {
    id: clientRow.id,
    name: `${clientRow.name_f} ${clientRow.name_l}`.trim(),
    name_f: clientRow.name_f,
    name_l: clientRow.name_l,
    email: clientRow.email,
    company: clientRow.company,
    phone: clientRow.phone,
    tax_id: clientRow.tax_id,
    address: serializeAddress(clientRow.address),
    note: clientRow.note,
    balance: clientRow.balance,
    spent: spent,
    optin: clientRow.optin,
    stripe_id: clientRow.stripe_id,
    custom_fields: clientRow.custom_fields,
    status: clientRow.status,
    aff_id: clientRow.aff_id,
    aff_link: clientRow.aff_link,
    role_id: clientRow.role_id,
    role: serializeRole(clientRow.role),
    ga_cid: clientRow.ga_cid,
    created_at: clientRow.created_at,
  };

  return NextResponse.json(response);
}
