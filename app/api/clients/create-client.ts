import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

interface CreateClientBody {
  name_f: string;
  name_l: string;
  email: string;
  company?: string | null;
  phone?: string | null;
  tax_id?: string | null;
  address?: {
    line_1?: string | null;
    line_2?: string | null;
    city?: string | null;
    state?: string | null;
    country?: string | null;
    postcode?: string | null;
  } | null;
  note?: string | null;
  optin?: string | null;
  stripe_id?: string | null;
  custom_fields?: Record<string, unknown>;
  status_id?: number;
  created_at?: string;
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

function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function generateAffiliateId(): number {
  return Math.floor(Math.random() * 900000) + 100000;
}

function generateAffiliateLink(): string {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  let code = "";
  for (let i = 0; i < 6; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return `https://example.com/r/${code}`;
}

export async function createClient(request: NextRequest) {
  let body: CreateClientBody;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      { message: "Invalid JSON body" },
      { status: 400 }
    );
  }

  const errors: Record<string, string[]> = {};

  if (!body.name_f || typeof body.name_f !== "string" || body.name_f.trim() === "") {
    errors.name_f = ["The name_f field is required."];
  }

  if (!body.name_l || typeof body.name_l !== "string" || body.name_l.trim() === "") {
    errors.name_l = ["The name_l field is required."];
  }

  if (!body.email || typeof body.email !== "string" || body.email.trim() === "") {
    errors.email = ["The email field is required."];
  } else if (!validateEmail(body.email)) {
    errors.email = ["The email must be a valid email address."];
  }

  if (Object.keys(errors).length > 0) {
    return NextResponse.json(
      { message: "The given data was invalid.", errors },
      { status: 400 }
    );
  }

  const { data: existingUser } = await supabase
    .from("users")
    .select("id")
    .eq("email", body.email.toLowerCase().trim())
    .single();

  if (existingUser) {
    return NextResponse.json(
      {
        message: "The given data was invalid.",
        errors: { email: ["The email has already been taken."] },
      },
      { status: 400 }
    );
  }

  const { data: clientRole } = await supabase
    .from("roles")
    .select("*")
    .eq("dashboard_access", 0)
    .single();

  if (!clientRole) {
    return NextResponse.json(
      { error: "Client role not configured" },
      { status: 500 }
    );
  }

  let addressId: string | null = null;
  let addressData: AddressRow | null = null;

  if (body.address && typeof body.address === "object") {
    const { data: newAddress, error: addressError } = await supabase
      .from("addresses")
      .insert({
        line_1: body.address.line_1 || null,
        line_2: body.address.line_2 || null,
        city: body.address.city || null,
        state: body.address.state || null,
        country: body.address.country || null,
        postcode: body.address.postcode || null,
        name_f: body.name_f,
        name_l: body.name_l,
        tax_id: body.tax_id || null,
        company_name: body.company || null,
        company_vat: null,
      })
      .select()
      .single();

    if (addressError) {
      return NextResponse.json(
        { error: "Failed to create address" },
        { status: 500 }
      );
    }

    addressId = newAddress.id;
    addressData = newAddress;
  }

  const affId = generateAffiliateId();
  const affLink = generateAffiliateLink();

  const { data: newUser, error: userError } = await supabase
    .from("users")
    .insert({
      email: body.email.toLowerCase().trim(),
      name_f: body.name_f.trim(),
      name_l: body.name_l.trim(),
      company: body.company || null,
      phone: body.phone || null,
      tax_id: body.tax_id || null,
      note: body.note || null,
      role_id: clientRole.id,
      status: body.status_id ?? 1,
      balance: "0.00",
      spent: "0.00",
      optin: body.optin || null,
      stripe_id: body.stripe_id || null,
      custom_fields: body.custom_fields || {},
      aff_id: affId,
      aff_link: affLink,
      ga_cid: null,
      address_id: addressId,
      created_at: body.created_at || new Date().toISOString(),
    })
    .select()
    .single();

  if (userError) {
    if (addressId) {
      await supabase.from("addresses").delete().eq("id", addressId);
    }
    return NextResponse.json(
      { error: "Failed to create client" },
      { status: 500 }
    );
  }

  const response = {
    id: newUser.id,
    name: `${newUser.name_f} ${newUser.name_l}`.trim(),
    name_f: newUser.name_f,
    name_l: newUser.name_l,
    email: newUser.email,
    company: newUser.company,
    phone: newUser.phone,
    tax_id: newUser.tax_id,
    address: serializeAddress(addressData),
    note: newUser.note,
    balance: newUser.balance,
    spent: null,
    optin: newUser.optin,
    stripe_id: newUser.stripe_id,
    custom_fields: newUser.custom_fields,
    status: newUser.status,
    aff_id: newUser.aff_id,
    aff_link: newUser.aff_link,
    role_id: newUser.role_id,
    role: serializeRole(clientRole),
    ga_cid: newUser.ga_cid,
    created_at: newUser.created_at,
  };

  return NextResponse.json(response, { status: 201 });
}
