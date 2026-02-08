import { supabase } from "@/lib/supabase";

const STATUS_MAP: Record<number, string> = {
  0: "Draft",
  1: "Unpaid",
  3: "Paid",
  4: "Refunded",
  5: "Cancelled",
  7: "Partially Paid",
};

export async function retrieveInvoice(
  id: string,
  orgId: string
): Promise<{ data?: unknown; error?: string; status: number }> {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(id)) {
    return { error: "Not Found", status: 404 };
  }

  const { data: invoice, error } = await supabase
    .from("invoices")
    .select(`
      *,
      users:user_id (
        id, name_f, name_l, email, company, phone, tax_id,
        aff_id, stripe_id, balance, custom_fields, status,
        addresses:address_id (*),
        roles:role_id (*)
      ),
      invoice_items (*)
    `)
    .eq("id", id)
    .eq("org_id", orgId)
    .is("deleted_at", null)
    .single();

  if (error || !invoice) {
    return { error: "Not Found", status: 404 };
  }

  const client = invoice.users as Record<string, unknown> | null;
  const items = invoice.invoice_items as Record<string, unknown>[] | null;
  const statusId = invoice.status as number;

  return {
    data: {
      id: invoice.id,
      number: invoice.number,
      number_prefix: invoice.number_prefix,
      client: client ? formatClient(client) : null,
      items: (items || []).map(formatItem),
      billing_address: invoice.billing_address,
      status: STATUS_MAP[statusId] || "Unknown",
      status_id: statusId,
      created_at: invoice.created_at,
      date_due: invoice.date_due,
      date_paid: invoice.date_paid,
      credit: invoice.credit,
      tax: invoice.tax,
      tax_name: invoice.tax_name,
      tax_percent: invoice.tax_percent,
      currency: invoice.currency,
      reason: invoice.reason,
      note: invoice.note,
      ip_address: invoice.ip_address,
      loc_confirm: invoice.loc_confirm,
      recurring: invoice.recurring,
      coupon_id: invoice.coupon_id,
      transaction_id: invoice.transaction_id,
      paysys: invoice.paysys,
      subtotal: invoice.subtotal,
      total: invoice.total,
      employee_id: invoice.employee_id,
      view_link: invoice.view_link,
      download_link: invoice.download_link,
      thanks_link: invoice.thanks_link,
    },
    status: 200,
  };
}

function formatClient(client: Record<string, unknown>): Record<string, unknown> {
  const addressArray = client.addresses as Record<string, unknown>[] | null;
  const address = Array.isArray(addressArray) ? addressArray[0] || null : null;
  const roleArray = client.roles as Record<string, unknown>[] | null;
  const role = Array.isArray(roleArray) ? roleArray[0] || null : null;

  return {
    id: client.id,
    aff_id: client.aff_id,
    name: `${client.name_f || ""} ${client.name_l || ""}`.trim(),
    name_f: client.name_f,
    name_l: client.name_l,
    email: client.email,
    company: client.company,
    phone: client.phone,
    tax_id: client.tax_id,
    address: address || null,
    balance: client.balance,
    stripe_id: client.stripe_id,
    custom_fields: client.custom_fields,
    status: client.status,
    role: role || null,
  };
}

function formatItem(item: Record<string, unknown>): Record<string, unknown> {
  return {
    id: item.id,
    invoice_id: item.invoice_id,
    name: item.name,
    description: item.description,
    quantity: item.quantity,
    amount: item.amount,
    discount: item.discount,
    discount2: item.discount2,
    total: item.total,
    service_id: item.service_id,
    order_id: item.order_id,
    options: item.options,
    created_at: item.created_at,
    updated_at: item.updated_at,
  };
}
