import { NextRequest } from "next/server";
import { listTickets } from "./list-tickets";
import { createTicket } from "./create-ticket";

export async function GET(request: NextRequest) {
  return listTickets(request);
}

export async function POST(request: NextRequest) {
  return createTicket(request);
}
