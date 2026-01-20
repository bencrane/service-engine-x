import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

interface MetadataItem {
  title: string;
  value: string;
}

interface UpdateServiceBody {
  name?: string;
  description?: string | null;
  recurring?: number;
  currency?: string;
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
  sort_order?: number;
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

export async function updateService(request: NextRequest, id: string) {
  if (!isValidUUID(id)) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  let body: UpdateServiceBody;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ message: "Invalid JSON body" }, { status: 400 });
  }

  const { data: existingService, error: fetchError } = await supabase
    .from("services")
    .select("*")
    .eq("id", id)
    .is("deleted_at", null)
    .single();

  if (fetchError || !existingService) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  const errors: Record<string, string[]> = {};

  if (body.name !== undefined) {
    if (typeof body.name !== "string" || body.name.trim() === "") {
      errors.name = ["The name field must be a non-empty string."];
    } else if (body.name.length > 255) {
      errors.name = ["The name may not be greater than 255 characters."];
    }
  }

  if (body.recurring !== undefined && ![0, 1, 2].includes(body.recurring)) {
    errors.recurring = ["The recurring field must be 0, 1, or 2."];
  }

  if (body.f_period_t !== undefined && !isValidPeriodType(body.f_period_t)) {
    errors.f_period_t = ["The period type must be D, W, M, or Y."];
  }

  if (body.r_period_t !== undefined && !isValidPeriodType(body.r_period_t)) {
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

  if (body.folder_id !== undefined && body.folder_id !== null) {
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

  if (body.employees !== undefined) {
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

  const updatePayload: Record<string, unknown> = {
    updated_at: new Date().toISOString(),
  };

  if (body.name !== undefined) updatePayload.name = body.name.trim();
  if (body.description !== undefined) updatePayload.description = body.description;
  if (body.recurring !== undefined) updatePayload.recurring = body.recurring;
  if (body.currency !== undefined) updatePayload.currency = body.currency.toUpperCase().trim();
  if (body.price !== undefined) updatePayload.price = body.price;
  if (body.f_price !== undefined) updatePayload.f_price = body.f_price;
  if (body.f_period_l !== undefined) updatePayload.f_period_l = body.f_period_l;
  if (body.f_period_t !== undefined) updatePayload.f_period_t = body.f_period_t;
  if (body.r_price !== undefined) updatePayload.r_price = body.r_price;
  if (body.r_period_l !== undefined) updatePayload.r_period_l = body.r_period_l;
  if (body.r_period_t !== undefined) updatePayload.r_period_t = body.r_period_t;
  if (body.recurring_action !== undefined) updatePayload.recurring_action = body.recurring_action;
  if (body.deadline !== undefined) updatePayload.deadline = body.deadline;
  if (body.public !== undefined) updatePayload.public = body.public;
  if (body.multi_order !== undefined) updatePayload.multi_order = body.multi_order;
  if (body.request_orders !== undefined) updatePayload.request_orders = body.request_orders;
  if (body.max_active_requests !== undefined) updatePayload.max_active_requests = body.max_active_requests;
  if (body.group_quantities !== undefined) updatePayload.group_quantities = body.group_quantities;
  if (body.folder_id !== undefined) updatePayload.folder_id = body.folder_id;
  if (body.sort_order !== undefined) updatePayload.sort_order = body.sort_order;
  if (body.braintree_plan_id !== undefined) updatePayload.braintree_plan_id = body.braintree_plan_id;
  if (body.hoth_product_key !== undefined) updatePayload.hoth_product_key = body.hoth_product_key;
  if (body.hoth_package_name !== undefined) updatePayload.hoth_package_name = body.hoth_package_name;
  if (body.provider_id !== undefined) updatePayload.provider_id = body.provider_id;
  if (body.provider_service_id !== undefined) updatePayload.provider_service_id = body.provider_service_id;

  if (body.metadata !== undefined) {
    if (body.metadata === null || (Array.isArray(body.metadata) && body.metadata.length === 0)) {
      updatePayload.metadata = {};
    } else {
      updatePayload.metadata = transformMetadata(body.metadata);
    }
  }

  const { data: updatedService, error: updateError } = await supabase
    .from("services")
    .update(updatePayload)
    .eq("id", id)
    .select()
    .single();

  if (updateError || !updatedService) {
    return NextResponse.json({ error: "Failed to update service" }, { status: 500 });
  }

  if (body.employees !== undefined) {
    await supabase.from("service_employees").delete().eq("service_id", id);

    if (body.employees.length > 0) {
      const employeeRows = body.employees.map((empId) => ({
        service_id: id,
        employee_id: empId,
      }));

      const { error: empError } = await supabase
        .from("service_employees")
        .insert(employeeRows);

      if (empError) {
        return NextResponse.json({ error: "Failed to update employees" }, { status: 500 });
      }
    }
  }

  const response = {
    id: updatedService.id,
    name: updatedService.name,
    description: updatedService.description,
    image: updatedService.image,
    recurring: updatedService.recurring,
    price: updatedService.price,
    pretty_price: formatPrettyPrice(updatedService.price, updatedService.currency),
    currency: updatedService.currency,
    f_price: updatedService.f_price,
    f_period_l: updatedService.f_period_l,
    f_period_t: updatedService.f_period_t,
    r_price: updatedService.r_price,
    r_period_l: updatedService.r_period_l,
    r_period_t: updatedService.r_period_t,
    recurring_action: updatedService.recurring_action,
    multi_order: updatedService.multi_order,
    request_orders: updatedService.request_orders,
    max_active_requests: updatedService.max_active_requests,
    deadline: updatedService.deadline,
    public: updatedService.public,
    sort_order: updatedService.sort_order,
    group_quantities: updatedService.group_quantities,
    folder_id: updatedService.folder_id,
    metadata: updatedService.metadata,
    braintree_plan_id: updatedService.braintree_plan_id,
    hoth_product_key: updatedService.hoth_product_key,
    hoth_package_name: updatedService.hoth_package_name,
    provider_id: updatedService.provider_id,
    provider_service_id: updatedService.provider_service_id,
    created_at: updatedService.created_at,
    updated_at: updatedService.updated_at,
  };

  return NextResponse.json(response);
}
