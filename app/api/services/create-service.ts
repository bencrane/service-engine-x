import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

interface MetadataItem {
  title: string;
  value: string;
}

interface CreateServiceBody {
  name: string;
  description?: string | null;
  recurring: number;
  currency: string;
  price?: number | null;
  f_price?: number | null;
  f_period_l?: number | null;
  f_period_t?: string | null;
  r_price?: number | null;
  r_period_l?: number | null;
  r_period_t?: string | null;
  recurring_action?: number | null;
  deadline?: number | null;
  public?: boolean;
  employees?: string[];
  group_quantities?: boolean;
  multi_order?: boolean;
  request_orders?: boolean;
  max_active_requests?: number | null;
  metadata?: MetadataItem[] | null;
  folder_id?: string | null;
  braintree_plan_id?: string | null;
  hoth_product_key?: string | null;
  hoth_package_name?: string | null;
  provider_id?: number | null;
  provider_service_id?: number | null;
}

function formatPrettyPrice(price: string | null, currency: string): string {
  const numPrice = parseFloat(price || "0");
  const symbols: Record<string, string> = {
    USD: "$",
    EUR: "€",
    GBP: "£",
    CAD: "CA$",
    AUD: "A$",
  };
  const symbol = symbols[currency] || `${currency} `;
  return `${symbol}${numPrice.toFixed(2)}`;
}

function transformMetadata(metadata: MetadataItem[] | null | undefined): Record<string, string> {
  if (!metadata || !Array.isArray(metadata)) return {};
  const result: Record<string, string> = {};
  for (const item of metadata) {
    if (item.title && typeof item.title === "string") {
      result[item.title] = String(item.value ?? "");
    }
  }
  return result;
}

function isValidPeriodType(value: string | null | undefined): boolean {
  if (value === null || value === undefined) return true;
  return ["D", "W", "M", "Y"].includes(value);
}

function isValidUUID(str: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

export async function createService(request: NextRequest) {
  let body: CreateServiceBody;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ message: "Invalid JSON body" }, { status: 400 });
  }

  const errors: Record<string, string[]> = {};

  if (!body.name || typeof body.name !== "string" || body.name.trim() === "") {
    errors.name = ["The name field is required."];
  } else if (body.name.length > 255) {
    errors.name = ["The name may not be greater than 255 characters."];
  }

  if (body.recurring === undefined || body.recurring === null) {
    errors.recurring = ["The recurring field is required."];
  } else if (![0, 1, 2].includes(body.recurring)) {
    errors.recurring = ["The recurring field must be 0, 1, or 2."];
  }

  if (!body.currency || typeof body.currency !== "string" || body.currency.trim() === "") {
    errors.currency = ["The currency field is required."];
  }

  if (!isValidPeriodType(body.f_period_t)) {
    errors.f_period_t = ["The period type must be D, W, M, or Y."];
  }

  if (!isValidPeriodType(body.r_period_t)) {
    errors.r_period_t = ["The period type must be D, W, M, or Y."];
  }

  if (body.metadata !== undefined && body.metadata !== null) {
    if (!Array.isArray(body.metadata)) {
      errors.metadata = ["The metadata must be an array of {title, value} objects."];
    } else {
      for (let i = 0; i < body.metadata.length; i++) {
        const item = body.metadata[i];
        if (!item.title || typeof item.title !== "string") {
          errors.metadata = [`Metadata item ${i} must have a title string.`];
          break;
        }
      }
    }
  }

  if (Object.keys(errors).length > 0) {
    return NextResponse.json({ message: "The given data was invalid.", errors }, { status: 400 });
  }

  if (body.folder_id) {
    if (!isValidUUID(body.folder_id)) {
      return NextResponse.json({
        message: "The given data was invalid.",
        errors: { folder_id: ["The specified folder does not exist."] },
      }, { status: 422 });
    }

    const { data: folder } = await supabase
      .from("service_folders")
      .select("id")
      .eq("id", body.folder_id)
      .single();

    if (!folder) {
      return NextResponse.json({
        message: "The given data was invalid.",
        errors: { folder_id: ["The specified folder does not exist."] },
      }, { status: 422 });
    }
  }

  if (body.employees && body.employees.length > 0) {
    for (const empId of body.employees) {
      if (!isValidUUID(empId)) {
        return NextResponse.json({
          message: "The given data was invalid.",
          errors: { employees: [`Employee with ID ${empId} does not exist.`] },
        }, { status: 422 });
      }

      const { data: emp } = await supabase
        .from("users")
        .select("id, role:roles(dashboard_access)")
        .eq("id", empId)
        .single();

      const role = emp?.role as { dashboard_access: number } | { dashboard_access: number }[] | null;
      const dashboardAccess = Array.isArray(role) ? role[0]?.dashboard_access : role?.dashboard_access;
      if (!emp || !role || dashboardAccess === 0) {
        return NextResponse.json({
          message: "The given data was invalid.",
          errors: { employees: [`Employee with ID ${empId} does not exist.`] },
        }, { status: 422 });
      }
    }
  }

  const metadataObj = transformMetadata(body.metadata);

  const { data: newService, error: serviceError } = await supabase
    .from("services")
    .insert({
      name: body.name.trim(),
      description: body.description ?? null,
      recurring: body.recurring,
      currency: body.currency.toUpperCase().trim(),
      price: body.price ?? null,
      f_price: body.f_price ?? null,
      f_period_l: body.f_period_l ?? null,
      f_period_t: body.f_period_t ?? null,
      r_price: body.r_price ?? null,
      r_period_l: body.r_period_l ?? null,
      r_period_t: body.r_period_t ?? null,
      recurring_action: body.recurring_action ?? null,
      deadline: body.deadline ?? null,
      public: body.public ?? true,
      multi_order: body.multi_order ?? true,
      request_orders: body.request_orders ?? false,
      max_active_requests: body.max_active_requests ?? null,
      group_quantities: body.group_quantities ?? false,
      folder_id: body.folder_id ?? null,
      metadata: metadataObj,
      braintree_plan_id: body.braintree_plan_id ?? null,
      hoth_product_key: body.hoth_product_key ?? null,
      hoth_package_name: body.hoth_package_name ?? null,
      provider_id: body.provider_id ?? null,
      provider_service_id: body.provider_service_id ?? null,
    })
    .select()
    .single();

  if (serviceError || !newService) {
    return NextResponse.json({ error: "Failed to create service" }, { status: 500 });
  }

  if (body.employees && body.employees.length > 0) {
    const employeeRows = body.employees.map((empId) => ({
      service_id: newService.id,
      employee_id: empId,
    }));

    const { error: empError } = await supabase
      .from("service_employees")
      .insert(employeeRows);

    if (empError) {
      await supabase.from("services").delete().eq("id", newService.id);
      return NextResponse.json({ error: "Failed to assign employees" }, { status: 500 });
    }
  }

  const response = {
    id: newService.id,
    name: newService.name,
    description: newService.description,
    image: newService.image,
    recurring: newService.recurring,
    price: newService.price,
    pretty_price: formatPrettyPrice(newService.price, newService.currency),
    currency: newService.currency,
    f_price: newService.f_price,
    f_period_l: newService.f_period_l,
    f_period_t: newService.f_period_t,
    r_price: newService.r_price,
    r_period_l: newService.r_period_l,
    r_period_t: newService.r_period_t,
    recurring_action: newService.recurring_action,
    multi_order: newService.multi_order,
    request_orders: newService.request_orders,
    max_active_requests: newService.max_active_requests,
    deadline: newService.deadline,
    public: newService.public,
    sort_order: newService.sort_order,
    group_quantities: newService.group_quantities,
    folder_id: newService.folder_id,
    metadata: newService.metadata,
    braintree_plan_id: newService.braintree_plan_id,
    hoth_product_key: newService.hoth_product_key,
    hoth_package_name: newService.hoth_package_name,
    provider_id: newService.provider_id,
    provider_service_id: newService.provider_service_id,
    created_at: newService.created_at,
    updated_at: newService.updated_at,
  };

  return NextResponse.json(response, { status: 201 });
}
