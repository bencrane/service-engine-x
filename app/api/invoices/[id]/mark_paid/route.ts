import { NextRequest, NextResponse } from "next/server";
import { markInvoicePaid } from "./mark-invoice-paid";

// POST /api/invoices/{id}/mark_paid
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  const result = await markInvoicePaid(id);

  if (result.error) {
    return NextResponse.json({ error: result.error }, { status: result.status });
  }

  return NextResponse.json(result.data, { status: 200 });
}
