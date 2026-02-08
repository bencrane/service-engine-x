import { supabase } from "@/lib/supabase";

interface ListInvoicesParams {
  limit?: number;
  page?: number;
  sort?: string;
  filters?: Record<string, Record<string, unknown>>;
}

const STATUS_MAP: Record<number, string> = {
  0: "Draft",
  1: "Unpaid",
  3: "Paid",
  4: "Refunded",
  5: "Cancelled",
  7: "Partially Paid",
};

export async function listInvoices(
  params: ListInvoicesParams,
  baseUrl: string,
  orgId: string
): Promise<{ data?: unknown; error?: string; status: number }> {
  const { limit = 20, page = 1, sort = "created_at:desc", filters = {} } = params;

  const validLimit = Math.max(1, Math.min(100, limit));
  const validPage = Math.max(1, page);
  const offset = (validPage - 1) * validLimit;

  // Parse sort
  const [sortField, sortDir] = sort.split(":");
  const ascending = sortDir === "asc";

  // Build query - exclude soft-deleted, filter by org
  let query = supabase
    .from("invoices")
    .select(`
      *,
      users:user_id (
        id, name_f, name_l, email, company, phone, tax_id,
        addresses:address_id (*),
        roles:role_id (*)
      ),
      invoice_items (*)
    `, { count: "exact" })
    .eq("org_id", orgId)
    .is("deleted_at", null);

  // Apply filters
  for (const [field, ops] of Object.entries(filters)) {
    for (const [op, value] of Object.entries(ops as Record<string, unknown>)) {
      if (op === "$eq") {
        query = query.eq(field, value);
      } else if (op === "$lt") {
        query = query.lt(field, value);
      } else if (op === "$gt") {
        query = query.gt(field, value);
      } else if (op === "$in" && Array.isArray(value)) {
        query = query.in(field, value);
      }
    }
  }

  // Apply sort
  query = query.order(sortField, { ascending });

  // Apply pagination
  query = query.range(offset, offset + validLimit - 1);

  const { data: invoices, count, error } = await query;

  if (error) {
    console.error("Failed to list invoices:", error);
    return { error: "Internal server error", status: 500 };
  }

  const total = count || 0;
  const lastPage = Math.ceil(total / validLimit) || 1;
  const path = `${baseUrl}/api/invoices`;

  const formattedInvoices = (invoices || []).map((inv) => formatInvoiceResponse(inv));

  return {
    data: {
      data: formattedInvoices,
      links: {
        first: `${path}?page=1&limit=${validLimit}`,
        last: `${path}?page=${lastPage}&limit=${validLimit}`,
        prev: validPage > 1 ? `${path}?page=${validPage - 1}&limit=${validLimit}` : null,
        next: validPage < lastPage ? `${path}?page=${validPage + 1}&limit=${validLimit}` : null,
      },
      meta: {
        current_page: validPage,
        from: total > 0 ? offset + 1 : 0,
        to: Math.min(offset + validLimit, total),
        last_page: lastPage,
        per_page: validLimit,
        total,
        path,
      },
    },
    status: 200,
  };
}

function formatInvoiceResponse(inv: Record<string, unknown>): Record<string, unknown> {
  const statusId = inv.status as number;
  const client = inv.users as Record<string, unknown> | null;
  const items = inv.invoice_items as Record<string, unknown>[] | null;

  return {
    id: inv.id,
    number: inv.number,
    number_prefix: inv.number_prefix,
    client: client ? formatClientResponse(client) : null,
    items: (items || []).map(formatItemResponse),
    billing_address: inv.billing_address,
    status: STATUS_MAP[statusId] || "Unknown",
    status_id: statusId,
    created_at: inv.created_at,
    date_due: inv.date_due,
    date_paid: inv.date_paid,
    credit: inv.credit,
    tax: inv.tax,
    tax_name: inv.tax_name,
    tax_percent: inv.tax_percent,
    currency: inv.currency,
    reason: inv.reason,
    note: inv.note,
    ip_address: inv.ip_address,
    loc_confirm: inv.loc_confirm,
    recurring: inv.recurring,
    coupon_id: inv.coupon_id,
    transaction_id: inv.transaction_id,
    paysys: inv.paysys,
    subtotal: inv.subtotal,
    total: inv.total,
    employee_id: inv.employee_id,
    view_link: inv.view_link,
    download_link: inv.download_link,
    thanks_link: inv.thanks_link,
  };
}

function formatClientResponse(client: Record<string, unknown>): Record<string, unknown> {
  const address = client.addresses as Record<string, unknown> | null;
  const role = client.roles as Record<string, unknown> | null;

  return {
    id: client.id,
    name: `${client.name_f || ""} ${client.name_l || ""}`.trim(),
    name_f: client.name_f,
    name_l: client.name_l,
    email: client.email,
    company: client.company,
    phone: client.phone,
    tax_id: client.tax_id,
    address: address || null,
    role: role || null,
  };
}

function formatItemResponse(item: Record<string, unknown>): Record<string, unknown> {
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
