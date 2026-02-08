import { NextRequest, NextResponse } from "next/server";
import { markInvoicePaid } from "./mark-invoice-paid";
import { validateApiToken, extractBearerToken } from "@/lib/auth";

// POST /api/invoices/{id}/mark_paid
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const token = extractBearerToken(request.headers.get("authorization"));
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const auth = await validateApiToken(token);
  if (!auth.valid || !auth.orgId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { id } = await params;

  const result = await markInvoicePaid(id, auth.orgId);

  if (result.error) {
    return NextResponse.json({ error: result.error }, { status: result.status });
  }

  return NextResponse.json(result.data, { status: 200 });
}
