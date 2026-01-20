import { NextRequest, NextResponse } from "next/server";
import { retrieveInvoice } from "./retrieve-invoice";
import { updateInvoice } from "./update-invoice";
import { deleteInvoice } from "./delete-invoice";

// GET /api/invoices/{id}
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const result = await retrieveInvoice(id);

  if (result.error) {
    return NextResponse.json({ error: result.error }, { status: result.status });
  }

  return NextResponse.json(result.data, { status: 200 });
}

// PUT /api/invoices/{id}
export async function PUT(
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

  const result = await updateInvoice(id, body);

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

// DELETE /api/invoices/{id}
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const result = await deleteInvoice(id);

  if (result.error) {
    return NextResponse.json({ error: result.error }, { status: result.status });
  }

  return new NextResponse(null, { status: 204 });
}
