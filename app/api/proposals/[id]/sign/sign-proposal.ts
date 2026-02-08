import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

const PROPOSAL_STATUS_MAP: Record<number, string> = {
  0: "Draft",
  1: "Sent",
  2: "Signed",
  3: "Rejected",
};

const ORDER_STATUS_MAP: Record<number, string> = {
  0: "Unpaid",
  1: "In Progress",
  2: "Completed",
  3: "Cancelled",
  4: "On Hold",
};

function isValidUUID(str: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

function generateOrderNumber(): string {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  let result = "";
  for (let i = 0; i < 8; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

export async function signProposal(id: string, orgId: string) {
  if (!isValidUUID(id)) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  // Fetch proposal with items
  const { data: proposal, error: fetchError } = await supabase
    .from("proposals")
    .select(`
      *,
      proposal_items (
        id,
        service_id,
        quantity,
        price,
        created_at,
        services:service_id (id, name, price, currency)
      )
    `)
    .eq("id", id)
    .eq("org_id", orgId)
    .is("deleted_at", null)
    .single();

  if (fetchError || !proposal) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  // Check if proposal can be signed (must be sent)
  if (proposal.status !== 1) {
    return NextResponse.json(
      { error: `Cannot sign proposal with status ${PROPOSAL_STATUS_MAP[proposal.status as number]}` },
      { status: 400 }
    );
  }

  const now = new Date().toISOString();
  const items = proposal.proposal_items as Array<{
    id: string;
    service_id: string;
    quantity: number;
    price: string;
    created_at: string;
    services: { id: string; name: string; price: string; currency: string } | null;
  }> | null;

  // Find or create client user
  let clientId: string | null = null;
  const { data: existingUser } = await supabase
    .from("users")
    .select("id")
    .eq("email", proposal.client_email)
    .eq("org_id", orgId)
    .single();

  if (existingUser) {
    clientId = existingUser.id;
  } else {
    // Get client role
    const { data: clientRole } = await supabase
      .from("roles")
      .select("id")
      .eq("dashboard_access", 0)
      .single();

    if (clientRole) {
      const { data: newUser } = await supabase
        .from("users")
        .insert({
          org_id: orgId,
          email: proposal.client_email,
          name_f: proposal.client_name_f,
          name_l: proposal.client_name_l,
          company: proposal.client_company,
          role_id: clientRole.id,
          status: 1,
          balance: "0.00",
          spent: "0.00",
          custom_fields: {},
        })
        .select("id")
        .single();

      if (newUser) {
        clientId = newUser.id;
      }
    }
  }

  // Create order from first item (primary service)
  const primaryItem = items?.[0];
  const serviceName = primaryItem?.services?.name || "Proposal Order";
  const servicePrice = primaryItem?.price || "0.00";
  const currency = primaryItem?.services?.currency || "USD";

  const { data: order, error: orderError } = await supabase
    .from("orders")
    .insert({
      org_id: orgId,
      number: generateOrderNumber(),
      user_id: clientId,
      service_id: primaryItem?.service_id || null,
      service_name: serviceName,
      price: proposal.total,
      currency: currency,
      quantity: 1,
      status: 0, // Unpaid
      note: `Created from proposal. ${proposal.notes || ""}`.trim(),
      form_data: {},
      metadata: {
        proposal_id: proposal.id,
        proposal_items: items?.map(item => ({
          service_id: item.service_id,
          service_name: item.services?.name,
          quantity: item.quantity,
          price: item.price,
        })),
      },
    })
    .select()
    .single();

  if (orderError || !order) {
    console.error("Failed to create order:", orderError);
    return NextResponse.json({ error: "Failed to create order" }, { status: 500 });
  }

  // Update proposal
  const { error: updateError } = await supabase
    .from("proposals")
    .update({
      status: 2,
      signed_at: now,
      updated_at: now,
      converted_order_id: order.id,
    })
    .eq("id", id);

  if (updateError) {
    console.error("Failed to update proposal:", updateError);
    // Clean up order
    await supabase.from("orders").delete().eq("id", order.id);
    return NextResponse.json({ error: "Failed to sign proposal" }, { status: 500 });
  }

  const proposalResponse = {
    id: proposal.id,
    client_email: proposal.client_email,
    client_name: `${proposal.client_name_f} ${proposal.client_name_l}`.trim(),
    client_name_f: proposal.client_name_f,
    client_name_l: proposal.client_name_l,
    client_company: proposal.client_company,
    status: "Signed",
    status_id: 2,
    total: proposal.total,
    notes: proposal.notes,
    created_at: proposal.created_at,
    updated_at: now,
    sent_at: proposal.sent_at,
    signed_at: now,
    converted_order_id: order.id,
    items: (items || []).map(item => ({
      id: item.id,
      service_id: item.service_id,
      service_name: item.services?.name || null,
      quantity: item.quantity,
      price: item.price,
      created_at: item.created_at,
    })),
  };

  const orderResponse = {
    id: order.id,
    number: order.number,
    user_id: order.user_id,
    service_id: order.service_id,
    service: order.service_name,
    price: order.price,
    currency: order.currency,
    quantity: order.quantity,
    status: ORDER_STATUS_MAP[order.status as number] || "Unknown",
    status_id: order.status,
    note: order.note,
    created_at: order.created_at,
  };

  return NextResponse.json({
    proposal: proposalResponse,
    order: orderResponse,
  });
}
