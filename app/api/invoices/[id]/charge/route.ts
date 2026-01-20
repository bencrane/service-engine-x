import { NextRequest, NextResponse } from "next/server";
import { chargeInvoice } from "./charge-invoice";

// POST /api/invoices/{id}/charge
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  let body;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  // Get client IP
  const clientIp = request.headers.get("x-forwarded-for")?.split(",")[0] || 
                   request.headers.get("x-real-ip") || 
                   "unknown";

  const result = await chargeInvoice(id, body, clientIp);

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

  return NextResponse.json(result.data, { status: 200 });
}
