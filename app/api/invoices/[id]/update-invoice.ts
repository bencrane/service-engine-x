import { supabase } from "@/lib/supabase";

interface InvoiceItemInput {
  id?: string;
  name: string;
  description?: string;
  quantity: number;
  amount: number;
  discount?: number;
  service_id?: string;
  options?: Record<string, unknown>;
}

interface UpdateInvoiceInput {
  user_id?: string;
  items: InvoiceItemInput[];
  status?: number;
  tax?: number;
  tax_type?: number;
  recurring?: { r_period_l: number; r_period_t: string } | null;
  coupon_id?: string | null;
  note?: string;
}

interface ValidationErrors {
  [key: string]: string[];
}

const VALID_STATUSES = [0, 1, 3, 4, 5, 7];

// Valid status transitions
const STATUS_TRANSITIONS: Record<number, number[]> = {
  0: [1, 5],           // Draft -> Unpaid, Cancelled
  1: [0, 5],           // Unpaid -> Draft, Cancelled
  3: [4],              // Paid -> Refunded only
  4: [],               // Refunded -> terminal
  5: [0, 1],           // Cancelled -> Draft, Unpaid
  7: [3, 4, 5],        // Partially Paid -> Paid, Refunded, Cancelled
};

const STATUS_MAP: Record<number, string> = {
  0: "Draft",
  1: "Unpaid",
  3: "Paid",
  4: "Refunded",
  5: "Cancelled",
  7: "Partially Paid",
};

export async function updateInvoice(
  id: string,
  input: UpdateInvoiceInput
): Promise<{ data?: unknown; error?: string; errors?: ValidationErrors; status: number }> {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(id)) {
    return { error: "Not Found", status: 404 };
  }

  // Fetch existing invoice
  const { data: existing, error: fetchError } = await supabase
    .from("invoices")
    .select("*, users:user_id (*)")
    .eq("id", id)
    .is("deleted_at", null)
    .single();

  if (fetchError || !existing) {
    return { error: "Not Found", status: 404 };
  }

  const errors: ValidationErrors = {};

  // Validate items (required for update)
  if (!input.items || !Array.isArray(input.items)) {
    errors.items = ["The items field is required."];
  } else if (input.items.length === 0) {
    errors.items = ["At least one item is required."];
  } else {
    input.items.forEach((item, idx) => {
      if (!item.name) errors[`items.${idx}.name`] = ["The name field is required."];
      if (item.quantity === undefined || item.quantity < 1) {
        errors[`items.${idx}.quantity`] = ["Quantity must be at least 1."];
      }
      if (item.amount === undefined) {
        errors[`items.${idx}.amount`] = ["The amount field is required."];
      }
    });
  }

  // Validate status
  if (input.status !== undefined) {
    if (!VALID_STATUSES.includes(input.status)) {
      errors.status = ["The selected status is invalid."];
    } else {
      const currentStatus = existing.status as number;
      if (input.status !== currentStatus) {
        const allowed = STATUS_TRANSITIONS[currentStatus] || [];
        if (!allowed.includes(input.status)) {
          errors.status = [`Cannot transition from ${STATUS_MAP[currentStatus]} to ${STATUS_MAP[input.status]}.`];
        }
      }
    }
  }

  // Validate recurring
  if (input.recurring !== undefined && input.recurring !== null) {
    if (!input.recurring.r_period_l || !input.recurring.r_period_t) {
      errors.recurring = ["Recurring requires r_period_l and r_period_t."];
    } else if (!["M", "W", "D"].includes(input.recurring.r_period_t)) {
      errors.recurring = ["r_period_t must be M, W, or D."];
    }
  }

  if (Object.keys(errors).length > 0) {
    return { error: "The given data was invalid.", errors, status: 400 };
  }

  // Validate user_id if changing
  let clientId = existing.user_id;
  if (input.user_id && input.user_id !== existing.user_id) {
    const { data: client } = await supabase
      .from("users")
      .select("id")
      .eq("id", input.user_id)
      .single();

    if (!client) {
      return {
        error: "The given data was invalid.",
        errors: { user_id: ["The specified client does not exist."] },
        status: 422,
      };
    }
    clientId = input.user_id;
  }

  // Validate coupon if provided
  if (input.coupon_id) {
    const { data: coupon } = await supabase
      .from("coupons")
      .select("id")
      .eq("id", input.coupon_id)
      .single();

    if (!coupon) {
      return {
        error: "The given data was invalid.",
        errors: { coupon_id: ["The specified coupon does not exist."] },
        status: 422,
      };
    }
  }

  // Calculate new totals
  let subtotal = 0;
  for (const item of input.items) {
    const itemTotal = item.quantity * item.amount - (item.discount || 0);
    subtotal += itemTotal;
  }
  const tax = input.tax ?? existing.tax;
  const total = subtotal + (tax as number);

  // Update invoice
  const updateData: Record<string, unknown> = {
    user_id: clientId,
    subtotal,
    total,
    updated_at: new Date().toISOString(),
  };

  if (input.status !== undefined) updateData.status = input.status;
  if (input.tax !== undefined) updateData.tax = input.tax;
  if (input.tax_type !== undefined) updateData.tax_type = input.tax_type;
  if (input.recurring !== undefined) updateData.recurring = input.recurring;
  if (input.coupon_id !== undefined) updateData.coupon_id = input.coupon_id;
  if (input.note !== undefined) updateData.note = input.note;

  const { error: updateError } = await supabase
    .from("invoices")
    .update(updateData)
    .eq("id", id);

  if (updateError) {
    console.error("Failed to update invoice:", updateError);
    return { error: "Internal server error", status: 500 };
  }

  // Full replacement of items
  await supabase.from("invoice_items").delete().eq("invoice_id", id);

  const itemRows = input.items.map((item) => ({
    invoice_id: id,
    name: item.name,
    description: item.description || null,
    quantity: item.quantity,
    amount: item.amount,
    discount: item.discount || 0,
    discount2: 0,
    total: item.quantity * item.amount - (item.discount || 0),
    service_id: item.service_id || null,
    order_id: null,
    options: item.options || {},
  }));

  const { data: newItems } = await supabase
    .from("invoice_items")
    .insert(itemRows)
    .select("*");

  // Fetch updated invoice
  const { data: updated } = await supabase
    .from("invoices")
    .select("*, users:user_id (*)")
    .eq("id", id)
    .single();

  const client = updated?.users as Record<string, unknown> | null;
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
      items: (newItems || []).map((item) => ({
        id: item.id,
        invoice_id: item.invoice_id,
        name: item.name,
        description: item.description,
        quantity: item.quantity,
        amount: item.amount,
        discount: item.discount,
        total: item.total,
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
      recurring: updated?.recurring,
      coupon_id: updated?.coupon_id,
      note: updated?.note,
    },
    status: 200,
  };
}
