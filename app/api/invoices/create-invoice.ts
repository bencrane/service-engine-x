import { supabase } from "@/lib/supabase";

interface InvoiceItemInput {
  name: string;
  description?: string;
  quantity: number;
  amount: number;
  discount?: number;
  service_id?: string;
  options?: Record<string, unknown>;
}

interface CreateInvoiceInput {
  user_id?: string;
  email?: string;
  items: InvoiceItemInput[];
  status?: number;
  tax?: number;
  tax_type?: number;
  recurring?: { r_period_l: number; r_period_t: string } | null;
  coupon_id?: string;
  note?: string;
  user_data?: Record<string, unknown>;
}

interface ValidationErrors {
  [key: string]: string[];
}

const VALID_STATUSES = [0, 1, 3, 4, 5, 7];

export async function createInvoice(
  input: CreateInvoiceInput,
  orgId: string
): Promise<{ data?: unknown; error?: string; errors?: ValidationErrors; status: number }> {
  const errors: ValidationErrors = {};

  // Validate user_id or email required
  if (!input.user_id && !input.email) {
    errors.user_id = ["Either user_id or email is required."];
  }

  // Validate items
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
  if (input.status !== undefined && !VALID_STATUSES.includes(input.status)) {
    errors.status = ["The selected status is invalid."];
  }

  // Validate recurring
  if (input.recurring) {
    if (!input.recurring.r_period_l || !input.recurring.r_period_t) {
      errors.recurring = ["Recurring requires r_period_l and r_period_t."];
    } else if (!["M", "W", "D"].includes(input.recurring.r_period_t)) {
      errors.recurring = ["r_period_t must be M, W, or D."];
    }
  }

  if (Object.keys(errors).length > 0) {
    return { error: "The given data was invalid.", errors, status: 400 };
  }

  // Resolve client
  let clientId = input.user_id;
  if (!clientId && input.email) {
    const { data: existingUser } = await supabase
      .from("users")
      .select("id")
      .eq("email", input.email)
      .single();

    if (existingUser) {
      clientId = existingUser.id;
    } else {
      // Create new client
      const { data: newUser, error: createError } = await supabase
        .from("users")
        .insert({
          email: input.email,
          name_f: input.user_data?.name_f || "",
          name_l: input.user_data?.name_l || "",
          ...input.user_data,
        })
        .select("id")
        .single();

      if (createError || !newUser) {
        return { error: "Failed to create client.", status: 500 };
      }
      clientId = newUser.id;
    }
  }

  // Validate client exists
  const { data: client, error: clientError } = await supabase
    .from("users")
    .select("id, name_f, name_l, company, address_id, addresses:address_id (*)")
    .eq("id", clientId)
    .single();

  if (clientError || !client) {
    return {
      error: "The given data was invalid.",
      errors: { user_id: ["The specified client does not exist."] },
      status: 422,
    };
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

  // Calculate totals
  let subtotal = 0;
  for (const item of input.items) {
    const itemTotal = item.quantity * item.amount - (item.discount || 0);
    subtotal += itemTotal;
  }
  const tax = input.tax || 0;
  const total = subtotal + tax;

  // Generate invoice number
  const { count } = await supabase
    .from("invoices")
    .select("*", { count: "exact", head: true });
  const invoiceNumber = `INV-${String((count || 0) + 1).padStart(5, "0")}`;

  // Snapshot billing address
  const addressArray = client.addresses as Record<string, unknown>[] | null;
  const clientAddress = Array.isArray(addressArray) && addressArray.length > 0 ? addressArray[0] : null;
  const billingAddress = clientAddress ? {
    line_1: clientAddress.line_1,
    line_2: clientAddress.line_2,
    city: clientAddress.city,
    state: clientAddress.state,
    postcode: clientAddress.postcode,
    country: clientAddress.country,
    name_f: client.name_f,
    name_l: client.name_l,
    company_name: client.company,
    company_vat: null,
    tax_id: null,
  } : null;

  // Calculate due date (14 days default)
  const dueDate = new Date();
  dueDate.setDate(dueDate.getDate() + 14);

  // Create invoice
  const invoiceData = {
    org_id: orgId,
    number: invoiceNumber,
    number_prefix: "INV-",
    user_id: clientId,
    billing_address: billingAddress,
    status: input.status ?? 1,
    created_at: new Date().toISOString(),
    date_due: dueDate.toISOString(),
    date_paid: null,
    credit: 0,
    tax,
    tax_name: input.tax_type ? "Tax" : null,
    tax_percent: input.tax_type === 2 ? input.tax : 0,
    currency: "USD",
    reason: null,
    note: input.note || null,
    ip_address: null,
    loc_confirm: false,
    recurring: input.recurring || null,
    coupon_id: input.coupon_id || null,
    transaction_id: null,
    paysys: null,
    subtotal,
    total,
    employee_id: null,
  };

  const { data: newInvoice, error: insertError } = await supabase
    .from("invoices")
    .insert(invoiceData)
    .select("*")
    .single();

  if (insertError || !newInvoice) {
    console.error("Failed to create invoice:", insertError);
    return { error: "Internal server error", status: 500 };
  }

  // Create invoice items
  const itemRows = input.items.map((item) => ({
    invoice_id: newInvoice.id,
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

  const { data: createdItems, error: itemsError } = await supabase
    .from("invoice_items")
    .insert(itemRows)
    .select("*");

  if (itemsError) {
    console.error("Failed to create invoice items:", itemsError);
  }

  // Fetch full invoice with relations
  return {
    data: formatInvoiceResponse(newInvoice, client, createdItems || []),
    status: 201,
  };
}

function formatInvoiceResponse(
  inv: Record<string, unknown>,
  client: Record<string, unknown>,
  items: Record<string, unknown>[]
): Record<string, unknown> {
  const STATUS_MAP: Record<number, string> = {
    0: "Draft",
    1: "Unpaid",
    3: "Paid",
    4: "Refunded",
    5: "Cancelled",
    7: "Partially Paid",
  };

  return {
    id: inv.id,
    number: inv.number,
    number_prefix: inv.number_prefix,
    client: {
      id: client.id,
      name: `${client.name_f || ""} ${client.name_l || ""}`.trim(),
      name_f: client.name_f,
      name_l: client.name_l,
      email: client.email,
      company: client.company,
    },
    items: items.map((item) => ({
      id: item.id,
      invoice_id: item.invoice_id,
      name: item.name,
      description: item.description,
      quantity: item.quantity,
      amount: item.amount,
      discount: item.discount,
      total: item.total,
      service_id: item.service_id,
      order_id: item.order_id,
      options: item.options,
    })),
    billing_address: inv.billing_address,
    status: STATUS_MAP[inv.status as number] || "Unknown",
    status_id: inv.status,
    created_at: inv.created_at,
    date_due: inv.date_due,
    date_paid: inv.date_paid,
    credit: inv.credit,
    tax: inv.tax,
    tax_name: inv.tax_name,
    tax_percent: inv.tax_percent,
    currency: inv.currency,
    subtotal: inv.subtotal,
    total: inv.total,
    recurring: inv.recurring,
    coupon_id: inv.coupon_id,
    note: inv.note,
    transaction_id: inv.transaction_id,
    paysys: inv.paysys,
  };
}
