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

export async function retrieveProposal(id: string, orgId: string) {
  if (!isValidUUID(id)) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  const { data: proposal, error } = await supabase
    .from("proposals")
    .select(`
      *,
      proposal_items (
        id,
        service_id,
        quantity,
        price,
        created_at,
        services:service_id (id, name, description)
      )
    `)
    .eq("id", id)
    .eq("org_id", orgId)
    .is("deleted_at", null)
    .single();

  if (error || !proposal) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  const items = proposal.proposal_items as Array<{
    id: string;
    service_id: string;
    quantity: number;
    price: string;
    created_at: string;
    services: { id: string; name: string; description: string | null } | null;
  }> | null;

  const response = {
    id: proposal.id,
    client_email: proposal.client_email,
    client_name: `${proposal.client_name_f} ${proposal.client_name_l}`.trim(),
    client_name_f: proposal.client_name_f,
    client_name_l: proposal.client_name_l,
    client_company: proposal.client_company,
    status: STATUS_MAP[proposal.status as number] || "Unknown",
    status_id: proposal.status,
    total: proposal.total,
    notes: proposal.notes,
    created_at: proposal.created_at,
    updated_at: proposal.updated_at,
    sent_at: proposal.sent_at,
    signed_at: proposal.signed_at,
    converted_order_id: proposal.converted_order_id,
    items: (items || []).map(item => ({
      id: item.id,
      service_id: item.service_id,
      service_name: item.services?.name || null,
      service_description: item.services?.description || null,
      quantity: item.quantity,
      price: item.price,
      created_at: item.created_at,
    })),
  };

  return NextResponse.json(response);
}
