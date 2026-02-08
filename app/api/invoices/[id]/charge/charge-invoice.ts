import { supabase } from "@/lib/supabase";

interface ChargeInvoiceInput {
  payment_method_id: string;
}

interface ValidationErrors {
  [key: string]: string[];
}

const STATUS_MAP: Record<number, string> = {
  0: "Draft",
  1: "Unpaid",
  3: "Paid",
  4: "Refunded",
  5: "Cancelled",
  7: "Partially Paid",
};

export async function chargeInvoice(
  id: string,
  input: ChargeInvoiceInput,
  clientIp: string,
  orgId: string
): Promise<{ data?: unknown; error?: string; errors?: ValidationErrors; status: number }> {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(id)) {
    return { error: "Not Found", status: 404 };
  }

  // Validate payment_method_id
  if (!input.payment_method_id) {
    return {
      error: "The given data was invalid.",
      errors: { payment_method_id: ["The payment_method_id field is required."] },
      status: 400,
    };
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

  // Check if already paid
  if (invoice.status === 3) {
    return {
      error: "The given data was invalid.",
      errors: { payment_method_id: ["Invoice is already paid."] },
      status: 400,
    };
  }

  // Check if invoice has client
  if (!invoice.user_id) {
    return {
      error: "The given data was invalid.",
      errors: { payment_method_id: ["Invoice has no client assigned."] },
      status: 400,
    };
  }

  // TODO: Integrate with Stripe to process payment
  // For now, simulate successful payment
  const transactionId = `txn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const now = new Date().toISOString();

  // Update invoice as paid
  const { error: updateError } = await supabase
    .from("invoices")
    .update({
      status: 3,
      date_paid: now,
      transaction_id: transactionId,
      paysys: "Stripe",
      ip_address: clientIp,
      updated_at: now,
    })
    .eq("id", id);

  if (updateError) {
    console.error("Failed to update invoice:", updateError);
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
        // Link item to order
        await supabase
          .from("invoice_items")
          .update({ order_id: order.id })
          .eq("id", item.id);
      }
    }
  }

  // Fetch updated invoice
  const { data: updated } = await supabase
    .from("invoices")
    .select("*, users:user_id (*), invoice_items (*)")
    .eq("id", id)
    .single();

  const client = updated?.users as Record<string, unknown> | null;
  const updatedItems = updated?.invoice_items as Record<string, unknown>[] | null;
  const statusId = updated?.status as number;

  return {
    data: {
      id: updated?.id,
      number: updated?.number,
      number_prefix: updated?.number_prefix,
      client: client ? {
        id: client.id,
        name: `${client.name_f || ""} ${client.name_l || ""}`.trim(),
        name_f: client.name_f,
        name_l: client.name_l,
        email: client.email,
      } : null,
      items: (updatedItems || []).map((item) => ({
        id: item.id,
        name: item.name,
        quantity: item.quantity,
        amount: item.amount,
        total: item.total,
        order_id: item.order_id,
      })),
      billing_address: updated?.billing_address,
      status: STATUS_MAP[statusId] || "Unknown",
      status_id: statusId,
      created_at: updated?.created_at,
      date_due: updated?.date_due,
      date_paid: updated?.date_paid,
      tax: updated?.tax,
      subtotal: updated?.subtotal,
      total: updated?.total,
      transaction_id: updated?.transaction_id,
      paysys: updated?.paysys,
      ip_address: updated?.ip_address,
    },
    status: 200,
  };
}
