import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

const STATUS_MAP: Record<number, string> = {
  0: "Draft",
  1: "Sent",
  2: "Signed",
  3: "Rejected",
};

interface ProposalRow {
  id: string;
  org_id: string;
  client_email: string;
  client_name_f: string;
  client_name_l: string;
  client_company: string | null;
  status: number;
  total: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
  sent_at: string | null;
  signed_at: string | null;
  converted_order_id: string | null;
}

function serializeProposal(proposal: ProposalRow) {
  return {
    id: proposal.id,
    client_email: proposal.client_email,
    client_name: `${proposal.client_name_f} ${proposal.client_name_l}`.trim(),
    client_name_f: proposal.client_name_f,
    client_name_l: proposal.client_name_l,
    client_company: proposal.client_company,
    status: STATUS_MAP[proposal.status] || "Unknown",
    status_id: proposal.status,
    total: proposal.total,
    notes: proposal.notes,
    created_at: proposal.created_at,
    updated_at: proposal.updated_at,
    sent_at: proposal.sent_at,
    signed_at: proposal.signed_at,
    converted_order_id: proposal.converted_order_id,
  };
}

export async function listProposals(request: NextRequest, orgId: string) {
  const { searchParams } = new URL(request.url);

  const limit = Math.min(Math.max(parseInt(searchParams.get("limit") || "20", 10), 1), 100);
  const page = Math.max(parseInt(searchParams.get("page") || "1", 10), 1);
  const offset = (page - 1) * limit;

  const sortParam = searchParams.get("sort") || "created_at:desc";
  const [sortField, sortDirection] = sortParam.split(":");
  const validSortFields = ["id", "client_email", "status", "total", "created_at", "sent_at", "signed_at"];
  const actualSortField = validSortFields.includes(sortField) ? sortField : "created_at";
  const ascending = sortDirection === "asc";

  // Build count query
  let countQuery = supabase
    .from("proposals")
    .select("*", { count: "exact", head: true })
    .eq("org_id", orgId)
    .is("deleted_at", null);

  // Build data query
  let query = supabase
    .from("proposals")
    .select("*")
    .eq("org_id", orgId)
    .is("deleted_at", null);

  // Apply filters
  const filterableFields = ["id", "status", "client_email", "created_at"];

  for (const [key, value] of searchParams.entries()) {
    const filterMatch = key.match(/^filters\[(\w+)\]\[(\$\w+)\](\[\])?$/);
    if (filterMatch) {
      const [, field, operator] = filterMatch;
      if (!filterableFields.includes(field)) continue;

      switch (operator) {
        case "$eq":
          countQuery = countQuery.eq(field, value);
          query = query.eq(field, value);
          break;
        case "$lt":
          countQuery = countQuery.lt(field, value);
          query = query.lt(field, value);
          break;
        case "$gt":
          countQuery = countQuery.gt(field, value);
          query = query.gt(field, value);
          break;
        case "$in":
          const inValues = searchParams.getAll(`filters[${field}][$in][]`);
          if (inValues.length > 0) {
            countQuery = countQuery.in(field, inValues);
            query = query.in(field, inValues);
          }
          break;
      }
    }
  }

  const { count: total } = await countQuery;

  query = query.order(actualSortField, { ascending });
  query = query.range(offset, offset + limit - 1);

  const { data: proposals, error } = await query;

  if (error) {
    console.error("Failed to list proposals:", error);
    return NextResponse.json({ error: "Database error" }, { status: 500 });
  }

  const totalCount = total || 0;
  const lastPage = Math.ceil(totalCount / limit) || 1;
  const baseUrl = request.url.split("?")[0];

  const response = {
    data: (proposals as ProposalRow[]).map(serializeProposal),
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

  for (let i = 1; i <= Math.min(lastPage, 10); i++) {
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
