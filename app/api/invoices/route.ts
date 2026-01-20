import { NextRequest, NextResponse } from "next/server";
import { listInvoices } from "./list-invoices";
import { createInvoice } from "./create-invoice";

// GET /api/invoices
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);

  const limit = parseInt(searchParams.get("limit") || "20", 10);
  const page = parseInt(searchParams.get("page") || "1", 10);
  const sort = searchParams.get("sort") || "created_at:desc";

  // Parse filters from query params
  const filters: Record<string, Record<string, unknown>> = {};
  for (const [key, value] of searchParams.entries()) {
    const match = key.match(/^filters\[(\w+)\]\[(\$\w+)\](\[\])?$/);
    if (match) {
      const field = match[1];
      const op = match[2];
      if (!filters[field]) filters[field] = {};
      
      if (match[3]) {
        // Array operator like $in
        if (!filters[field][op]) filters[field][op] = [];
        (filters[field][op] as unknown[]).push(value);
      } else {
        filters[field][op] = value;
      }
    }
  }

  const baseUrl = new URL(request.url).origin;
  const result = await listInvoices({ limit, page, sort, filters }, baseUrl);

  if (result.error) {
    return NextResponse.json({ error: result.error }, { status: result.status });
  }

  return NextResponse.json(result.data, { status: 200 });
}

// POST /api/invoices
export async function POST(request: NextRequest) {
  let body;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const result = await createInvoice(body);

  if (result.error) {
    const response: { error?: string; message?: string; errors?: Record<string, string[]> } = {};
    if (result.errors) {
      response.message = result.error;
      response.errors = result.errors;
    } else {
      response.error = result.error;
    }
    return NextResponse.json(response, { status: result.status });
  }

  return NextResponse.json(result.data, { status: 201 });
}
