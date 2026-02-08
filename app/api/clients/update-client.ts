import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

interface UpdateClientBody {
  name_f?: string;
  name_l?: string;
  email?: string;
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

function isValidUUID(str: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export async function updateClient(request: NextRequest, id: string, orgId: string) {
  if (!isValidUUID(id)) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  let body: UpdateClientBody;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ message: "Invalid JSON body" }, { status: 400 });
  }

  const { data: clientRole } = await supabase
    .from("roles")
    .select("*")
    .eq("dashboard_access", 0)
    .single();

  if (!clientRole) {
    return NextResponse.json({ error: "Client role not configured" }, { status: 500 });
  }

  const { data: existingClient, error: fetchError } = await supabase
    .from("users")
    .select("*")
    .eq("id", id)
    .eq("org_id", orgId)
    .eq("role_id", clientRole.id)
    .single();

  if (fetchError || !existingClient) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  const errors: Record<string, string[]> = {};

  if (body.email !== undefined) {
    if (typeof body.email !== "string" || body.email.trim() === "") {
      errors.email = ["The email field must be a non-empty string."];
    } else if (!validateEmail(body.email)) {
      errors.email = ["The email must be a valid email address."];
    } else {
      const { data: duplicate } = await supabase
        .from("users")
        .select("id")
        .eq("email", body.email.toLowerCase().trim())
        .neq("id", id)
        .single();

      if (duplicate) {
        errors.email = ["The email has already been taken."];
      }
    }
  }

  if (Object.keys(errors).length > 0) {
    return NextResponse.json(
      { message: "The given data was invalid.", errors },
      { status: 400 }
    );
  }

  let addressId = existingClient.address_id;
  let addressData: AddressRow | null = null;

  if (body.address === null) {
    addressId = null;
  } else if (body.address !== undefined && typeof body.address === "object") {
    const addressPayload = {
      line_1: body.address.line_1 ?? null,
      line_2: body.address.line_2 ?? null,
      city: body.address.city ?? null,
      state: body.address.state ?? null,
      country: body.address.country ?? null,
      postcode: body.address.postcode ?? null,
      name_f: body.name_f ?? existingClient.name_f,
      name_l: body.name_l ?? existingClient.name_l,
      tax_id: body.tax_id ?? existingClient.tax_id,
      company_name: body.company ?? existingClient.company,
      company_vat: null,
    };

    if (existingClient.address_id) {
      const { data: updatedAddress, error: updateAddressError } = await supabase
        .from("addresses")
        .update(addressPayload)
        .eq("id", existingClient.address_id)
        .select()
        .single();

      if (updateAddressError) {
        return NextResponse.json({ error: "Failed to update address" }, { status: 500 });
      }
      addressData = updatedAddress;
    } else {
      const { data: newAddress, error: createAddressError } = await supabase
        .from("addresses")
        .insert(addressPayload)
        .select()
        .single();

      if (createAddressError) {
        return NextResponse.json({ error: "Failed to create address" }, { status: 500 });
      }
      addressId = newAddress.id;
      addressData = newAddress;
    }
  } else {
    if (existingClient.address_id) {
      const { data: existingAddress } = await supabase
        .from("addresses")
        .select("*")
        .eq("id", existingClient.address_id)
        .single();
      addressData = existingAddress;
    }
  }

  const updatePayload: Record<string, unknown> = {
    updated_at: new Date().toISOString(),
  };

  if (body.name_f !== undefined) updatePayload.name_f = body.name_f.trim();
  if (body.name_l !== undefined) updatePayload.name_l = body.name_l.trim();
  if (body.email !== undefined) updatePayload.email = body.email.toLowerCase().trim();
  if (body.company !== undefined) updatePayload.company = body.company;
  if (body.phone !== undefined) updatePayload.phone = body.phone;
  if (body.tax_id !== undefined) updatePayload.tax_id = body.tax_id;
  if (body.note !== undefined) updatePayload.note = body.note;
  if (body.optin !== undefined) updatePayload.optin = body.optin;
  if (body.stripe_id !== undefined) updatePayload.stripe_id = body.stripe_id;
  if (body.custom_fields !== undefined) updatePayload.custom_fields = body.custom_fields;
  if (body.status_id !== undefined) updatePayload.status = body.status_id;
  if (body.created_at !== undefined) updatePayload.created_at = body.created_at;
  if (body.address !== undefined) updatePayload.address_id = addressId;

  const { data: updatedUser, error: updateError } = await supabase
    .from("users")
    .update(updatePayload)
    .eq("id", id)
    .select()
    .single();

  if (updateError) {
    return NextResponse.json({ error: "Failed to update client" }, { status: 500 });
  }

  const { data: spentData } = await supabase
    .from("invoices")
    .select("total")
    .eq("user_id", id)
    .not("date_paid", "is", null);

  const spent = spentData && spentData.length > 0
    ? spentData.reduce((sum, inv) => sum + parseFloat(inv.total || "0"), 0).toFixed(2)
    : null;

  const response = {
    id: updatedUser.id,
    name: `${updatedUser.name_f} ${updatedUser.name_l}`.trim(),
    name_f: updatedUser.name_f,
    name_l: updatedUser.name_l,
    email: updatedUser.email,
    company: updatedUser.company,
    phone: updatedUser.phone,
    tax_id: updatedUser.tax_id,
    address: serializeAddress(addressData),
    note: updatedUser.note,
    balance: updatedUser.balance,
    spent: spent,
    optin: updatedUser.optin,
    stripe_id: updatedUser.stripe_id,
    custom_fields: updatedUser.custom_fields,
    status: updatedUser.status,
    aff_id: updatedUser.aff_id,
    aff_link: updatedUser.aff_link,
    role_id: updatedUser.role_id,
    role: serializeRole(clientRole),
    ga_cid: updatedUser.ga_cid,
    created_at: updatedUser.created_at,
  };

  return NextResponse.json(response);
}
