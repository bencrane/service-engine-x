import { NextRequest } from "next/server";
import { retrieveTicket } from "../retrieve-ticket";
import { updateTicket } from "../update-ticket";
import { deleteTicket } from "../delete-ticket";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  return retrieveTicket(id);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  return updateTicket(request, id);
}

export async function DELETE(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  return deleteTicket(id);
}
