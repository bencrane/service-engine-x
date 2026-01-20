import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

interface ServiceRow {
  id: string;
  name: string;
  description: string | null;
  image: string | null;
  recurring: number;
  price: string | null;
  currency: string;
  f_price: string | null;
  f_period_l: number | null;
  f_period_t: string | null;
  r_price: string | null;
  r_period_l: number | null;
  r_period_t: string | null;
  recurring_action: number | null;
  deadline: number | null;
  public: boolean;
  sort_order: number;
  multi_order: boolean;
  request_orders: boolean;
  max_active_requests: number | null;
  group_quantities: boolean;
  folder_id: string | null;
  metadata: Record<string, unknown>;
  braintree_plan_id: string | null;
  hoth_product_key: string | null;
  hoth_package_name: string | null;
  provider_id: number | null;
  provider_service_id: number | null;
  created_at: string;
  updated_at: string;
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

function serializeService(service: ServiceRow) {
  return {
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
}

export async function listServices(request: NextRequest) {
  const { searchParams } = new URL(request.url);

  const limit = Math.min(Math.max(parseInt(searchParams.get("limit") || "20", 10), 1), 100);
  const page = Math.max(parseInt(searchParams.get("page") || "1", 10), 1);
  const offset = (page - 1) * limit;

  const sortParam = searchParams.get("sort") || "created_at:desc";
  const [sortField, sortDirection] = sortParam.split(":");
  const validSortFields = ["id", "name", "price", "recurring", "public", "sort_order", "created_at"];
  const actualSortField = validSortFields.includes(sortField) ? sortField : "created_at";
  const ascending = sortDirection === "asc";

  let query = supabase
    .from("services")
    .select("*", { count: "exact" })
    .is("deleted_at", null);

  const filterableFields = ["id", "name", "recurring", "public", "price", "currency", "folder_id", "created_at"];

  for (const [key, value] of searchParams.entries()) {
    const filterMatch = key.match(/^filters\[(\w+)\]\[(\$\w+)\](\[\])?$/);
    if (filterMatch) {
      const [, field, operator] = filterMatch;
      if (!filterableFields.includes(field)) continue;

      switch (operator) {
        case "$eq":
          if (value === "null") {
            query = query.is(field, null);
          } else if (value === "true" || value === "false") {
            query = query.eq(field, value === "true");
          } else {
            query = query.eq(field, value);
          }
          break;
        case "$lt":
          query = query.lt(field, value);
          break;
        case "$gt":
          query = query.gt(field, value);
          break;
        case "$in":
          const inValues = searchParams.getAll(`filters[${field}][$in][]`);
          if (inValues.length > 0) {
            query = query.in(field, inValues);
          }
          break;
      }
    }
  }

  query = query.order(actualSortField, { ascending });

  const { count: total } = await query;

  query = supabase
    .from("services")
    .select("*")
    .is("deleted_at", null);

  for (const [key, value] of searchParams.entries()) {
    const filterMatch = key.match(/^filters\[(\w+)\]\[(\$\w+)\](\[\])?$/);
    if (filterMatch) {
      const [, field, operator] = filterMatch;
      if (!filterableFields.includes(field)) continue;

      switch (operator) {
        case "$eq":
          if (value === "null") {
            query = query.is(field, null);
          } else if (value === "true" || value === "false") {
            query = query.eq(field, value === "true");
          } else {
            query = query.eq(field, value);
          }
          break;
        case "$lt":
          query = query.lt(field, value);
          break;
        case "$gt":
          query = query.gt(field, value);
          break;
        case "$in":
          const inValues = searchParams.getAll(`filters[${field}][$in][]`);
          if (inValues.length > 0) {
            query = query.in(field, inValues);
          }
          break;
      }
    }
  }

  query = query.order(actualSortField, { ascending });
  query = query.range(offset, offset + limit - 1);

  const { data: services, error } = await query;

  if (error) {
    return NextResponse.json({ error: "Database error" }, { status: 500 });
  }

  const totalCount = total || 0;
  const lastPage = Math.ceil(totalCount / limit) || 1;

  const baseUrl = request.url.split("?")[0];

  const response = {
    data: (services as ServiceRow[]).map(serializeService),
    links: {
      first: `${baseUrl}?page=1&limit=${limit}`,
      last: `${baseUrl}?page=${lastPage}&limit=${limit}`,
      prev: page > 1 ? `${baseUrl}?page=${page - 1}&limit=${limit}` : null,
      next: page < lastPage ? `${baseUrl}?page=${page + 1}&limit=${limit}` : null,
    },
    meta: {
      current_page: page,
      from: totalCount > 0 ? offset + 1 : 0,
      to: Math.min(offset + limit, totalCount),
      last_page: lastPage,
      per_page: limit,
      total: totalCount,
      path: baseUrl,
      links: buildPaginationLinks(page, lastPage, baseUrl, limit),
    },
  };

  return NextResponse.json(response);
}

function buildPaginationLinks(currentPage: number, lastPage: number, baseUrl: string, limit: number) {
  const links: { url: string | null; label: string; active: boolean }[] = [];

  links.push({
    url: currentPage > 1 ? `${baseUrl}?page=${currentPage - 1}&limit=${limit}` : null,
    label: "Previous",
    active: false,
  });

  for (let i = 1; i <= lastPage; i++) {
    links.push({
      url: `${baseUrl}?page=${i}&limit=${limit}`,
      label: String(i),
      active: i === currentPage,
    });
  }

  links.push({
    url: currentPage < lastPage ? `${baseUrl}?page=${currentPage + 1}&limit=${limit}` : null,
    label: "Next",
    active: false,
  });

  return links;
}
