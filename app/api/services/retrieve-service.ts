import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

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

function isValidUUID(str: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

export async function retrieveService(id: string) {
  if (!isValidUUID(id)) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  const { data: service, error } = await supabase
    .from("services")
    .select("*")
    .eq("id", id)
    .is("deleted_at", null)
    .single();

  if (error || !service) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  const response = {
    id: service.id,
    name: service.name,
    description: service.description,
    image: service.image,
    recurring: service.recurring,
    price: service.price,
    pretty_price: formatPrettyPrice(service.price, service.currency),
    currency: service.currency,
    f_price: service.f_price,
    f_period_l: service.f_period_l,
    f_period_t: service.f_period_t,
    r_price: service.r_price,
    r_period_l: service.r_period_l,
    r_period_t: service.r_period_t,
    recurring_action: service.recurring_action,
    multi_order: service.multi_order,
    request_orders: service.request_orders,
    max_active_requests: service.max_active_requests,
    deadline: service.deadline,
    public: service.public,
    sort_order: service.sort_order,
    group_quantities: service.group_quantities,
    folder_id: service.folder_id,
    metadata: service.metadata,
    braintree_plan_id: service.braintree_plan_id,
    hoth_product_key: service.hoth_product_key,
    hoth_package_name: service.hoth_package_name,
    provider_id: service.provider_id,
    provider_service_id: service.provider_service_id,
    created_at: service.created_at,
    updated_at: service.updated_at,
  };

  return NextResponse.json(response);
}
