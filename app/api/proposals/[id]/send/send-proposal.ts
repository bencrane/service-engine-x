import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

const STATUS_MAP: Record<number, string> = {
  0: "Draft",
  1: "Sent",
  2: "Signed",
  3: "Rejected",
};

function isValidUUID(str: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

export async function sendProposal(id: string, orgId: string) {
  if (!isValidUUID(id)) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  // Fetch proposal
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
        services:service_id (id, name)
      )
    `)
    .eq("id", id)
    .eq("org_id", orgId)
    .is("deleted_at", null)
    .single();

  if (fetchError || !proposal) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  // Check if proposal can be sent (must be draft)
  if (proposal.status !== 0) {
    return NextResponse.json(
      { error: `Cannot send proposal with status ${STATUS_MAP[proposal.status as number]}` },
      { status: 400 }
    );
  }

  // Update proposal
  const now = new Date().toISOString();
  const { error: updateError } = await supabase
    .from("proposals")
    .update({
      status: 1,
      sent_at: now,
      updated_at: now,
    })
    .eq("id", id);

  if (updateError) {
    console.error("Failed to send proposal:", updateError);
    return NextResponse.json({ error: "Failed to send proposal" }, { status: 500 });
  }

  const items = proposal.proposal_items as Array<{
    id: string;
    service_id: string;
    quantity: number;
    price: string;
    created_at: string;
    services: { id: string; name: string } | null;
  }> | null;

  const response = {
    id: proposal.id,
    client_email: proposal.client_email,
    client_name: `${proposal.client_name_f} ${proposal.client_name_l}`.trim(),
    client_name_f: proposal.client_name_f,
    client_name_l: proposal.client_name_l,
    client_company: proposal.client_company,
    status: "Sent",
    status_id: 1,
    total: proposal.total,
    notes: proposal.notes,
    created_at: proposal.created_at,
    updated_at: now,
    sent_at: now,
    signed_at: proposal.signed_at,
    converted_order_id: proposal.converted_order_id,
    items: (items || []).map(item => ({
      id: item.id,
      service_id: item.service_id,
      service_name: item.services?.name || null,
      quantity: item.quantity,
      price: item.price,
      created_at: item.created_at,
    })),
  };

  return NextResponse.json(response);
}
