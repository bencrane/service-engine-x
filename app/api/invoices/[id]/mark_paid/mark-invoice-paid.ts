import { supabase } from "@/lib/supabase";

const STATUS_MAP: Record<number, string> = {
  0: "Draft",
  1: "Unpaid",
  3: "Paid",
  4: "Refunded",
  5: "Cancelled",
  7: "Partially Paid",
};

export async function markInvoicePaid(
  id: string,
  orgId: string
): Promise<{ data?: unknown; error?: string; status: number }> {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(id)) {
    return { error: "Not Found", status: 404 };
  }

  // Fetch invoice
  const { data: invoice, error: fetchError } = await supabase
    .from("invoices")
    .select("*, users:user_id (*), invoice_items (*)")
    .eq("id", id)
    .eq("org_id", orgId)
    .is("deleted_at", null)
    .single();

  if (fetchError || !invoice) {
    return { error: "Not Found", status: 404 };
  }

  // Idempotent: if already paid, return current state
  if (invoice.status === 3) {
    return {
      data: formatInvoiceResponse(invoice),
      status: 200,
    };
  }

  // Check if invoice has client
  if (!invoice.user_id) {
    return { error: "Invoice has no client assigned.", status: 400 };
  }

  // Check if invoice is in valid state to be marked paid
  if (invoice.status === 4 || invoice.status === 5) {
    return { error: `Cannot mark ${STATUS_MAP[invoice.status]} invoice as paid.`, status: 400 };
  }

  const now = new Date().toISOString();

  // Update invoice as paid (manual)
  const { error: updateError } = await supabase
    .from("invoices")
    .update({
      status: 3,
      date_paid: now,
      paysys: "Manual",
      updated_at: now,
    })
    .eq("id", id);

  if (updateError) {
    console.error("Failed to mark invoice paid:", updateError);
    return { error: "Internal server error", status: 500 };
  }

  // Create orders for items with service_id
  const items = invoice.invoice_items as Record<string, unknown>[];
  for (const item of items) {
    if (item.service_id) {
      const { data: order } = await supabase
        .from("orders")
        .insert({
          org_id: orgId,
          user_id: invoice.user_id,
          service_id: item.service_id,
          invoice_id: invoice.id,
          status: 0,
          quantity: item.quantity,
          price: item.amount,
          currency: invoice.currency,
        })
        .select("id")
        .single();

      if (order) {
        await supabase
          .from("invoice_items")
          .update({ order_id: order.id })
          .eq("id", item.id);
      }
    }
  }

  // Create subscription if recurring
  if (invoice.recurring) {
    const recurring = invoice.recurring as { r_period_l: number; r_period_t: string };
    await supabase.from("subscriptions").insert({
      org_id: orgId,
      user_id: invoice.user_id,
      invoice_id: invoice.id,
      status: 1,
      r_period_l: recurring.r_period_l,
      r_period_t: recurring.r_period_t,
    });
  }

  // Fetch updated invoice
  const { data: updated } = await supabase
    .from("invoices")
    .select("*, users:user_id (*), invoice_items (*)")
    .eq("id", id)
    .single();

  return {
    data: formatInvoiceResponse(updated),
    status: 200,
  };
}

function formatInvoiceResponse(invoice: Record<string, unknown>): Record<string, unknown> {
  const client = invoice.users as Record<string, unknown> | null;
  const items = invoice.invoice_items as Record<string, unknown>[] | null;
  const statusId = invoice.status as number;

  return {
    id: invoice.id,
    number: invoice.number,
    number_prefix: invoice.number_prefix,
    client: client ? {
      id: client.id,
      name: `${client.name_f || ""} ${client.name_l || ""}`.trim(),
      name_f: client.name_f,
      name_l: client.name_l,
      email: client.email,
    } : null,
    items: (items || []).map((item) => ({
      id: item.id,
      name: item.name,
      quantity: item.quantity,
      amount: item.amount,
      total: item.total,
      order_id: item.order_id,
    })),
    billing_address: invoice.billing_address,
    status: STATUS_MAP[statusId] || "Unknown",
    status_id: statusId,
    created_at: invoice.created_at,
    date_due: invoice.date_due,
    date_paid: invoice.date_paid,
    tax: invoice.tax,
    subtotal: invoice.subtotal,
    total: invoice.total,
    transaction_id: invoice.transaction_id,
    paysys: invoice.paysys,
    recurring: invoice.recurring,
  };
}
