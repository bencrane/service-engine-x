import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

const STATUS_MAP: Record<number, string> = {
  0: "Draft",
  1: "Sent",
  2: "Signed",
  3: "Rejected",
};

interface ProposalItemInput {
  service_id: string;
  quantity?: number;
  price: number;
}

interface CreateProposalBody {
  client_email: string;
  client_name_f: string;
  client_name_l: string;
  client_company?: string | null;
  items: ProposalItemInput[];
  notes?: string | null;
}

function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function isValidUUID(str: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

export async function createProposal(request: NextRequest, orgId: string) {
  let body: CreateProposalBody;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      { message: "Invalid JSON body" },
      { status: 400 }
    );
  }

  const errors: Record<string, string[]> = {};

  // Validate required fields
  if (!body.client_email || typeof body.client_email !== "string" || body.client_email.trim() === "") {
    errors.client_email = ["The client_email field is required."];
  } else if (!validateEmail(body.client_email)) {
    errors.client_email = ["The client_email must be a valid email address."];
  }

  if (!body.client_name_f || typeof body.client_name_f !== "string" || body.client_name_f.trim() === "") {
    errors.client_name_f = ["The client_name_f field is required."];
  }

  if (!body.client_name_l || typeof body.client_name_l !== "string" || body.client_name_l.trim() === "") {
    errors.client_name_l = ["The client_name_l field is required."];
  }

  // Validate items
  if (!body.items || !Array.isArray(body.items)) {
    errors.items = ["The items field is required and must be an array."];
  } else if (body.items.length === 0) {
    errors.items = ["At least one item is required."];
  } else {
    for (let i = 0; i < body.items.length; i++) {
      const item = body.items[i];
      if (!item.service_id) {
        errors[`items.${i}.service_id`] = ["The service_id field is required."];
      } else if (!isValidUUID(item.service_id)) {
        errors[`items.${i}.service_id`] = ["The service_id must be a valid UUID."];
      }
      if (item.price === undefined || item.price === null) {
        errors[`items.${i}.price`] = ["The price field is required."];
      } else if (typeof item.price !== "number" || item.price < 0) {
        errors[`items.${i}.price`] = ["The price must be a non-negative number."];
      }
      if (item.quantity !== undefined && (typeof item.quantity !== "number" || item.quantity < 1)) {
        errors[`items.${i}.quantity`] = ["The quantity must be at least 1."];
      }
    }
  }

  if (Object.keys(errors).length > 0) {
    return NextResponse.json(
      { message: "The given data was invalid.", errors },
      { status: 400 }
    );
  }

  // Validate all service_ids exist and belong to org
  const serviceIds = body.items.map(item => item.service_id);
  const { data: services, error: servicesError } = await supabase
    .from("services")
    .select("id")
    .eq("org_id", orgId)
    .is("deleted_at", null)
    .in("id", serviceIds);

  if (servicesError) {
    console.error("Failed to validate services:", servicesError);
    return NextResponse.json({ error: "Database error" }, { status: 500 });
  }

  const foundServiceIds = new Set(services?.map(s => s.id) || []);
  const missingServices = serviceIds.filter(id => !foundServiceIds.has(id));
  if (missingServices.length > 0) {
    return NextResponse.json(
      {
        message: "The given data was invalid.",
        errors: { items: [`Service with ID ${missingServices[0]} does not exist.`] },
      },
      { status: 422 }
    );
  }

  // Calculate total from items
  let total = 0;
  for (const item of body.items) {
    const quantity = item.quantity || 1;
    total += quantity * item.price;
  }

  // Create proposal
  const { data: proposal, error: proposalError } = await supabase
    .from("proposals")
    .insert({
      org_id: orgId,
      client_email: body.client_email.toLowerCase().trim(),
      client_name_f: body.client_name_f.trim(),
      client_name_l: body.client_name_l.trim(),
      client_company: body.client_company || null,
      status: 0, // Draft
      total: total,
      notes: body.notes || null,
    })
    .select()
    .single();

  if (proposalError || !proposal) {
    console.error("Failed to create proposal:", proposalError);
    return NextResponse.json({ error: "Failed to create proposal" }, { status: 500 });
  }

  // Create proposal items
  const itemRows = body.items.map(item => ({
    proposal_id: proposal.id,
    service_id: item.service_id,
    quantity: item.quantity || 1,
    price: item.price,
  }));

  const { data: proposalItems, error: itemsError } = await supabase
    .from("proposal_items")
    .insert(itemRows)
    .select(`
      id,
      proposal_id,
      service_id,
      quantity,
      price,
      created_at,
      services:service_id (id, name)
    `);

  if (itemsError) {
    console.error("Failed to create proposal items:", itemsError);
    // Clean up the proposal
    await supabase.from("proposals").delete().eq("id", proposal.id);
    return NextResponse.json({ error: "Failed to create proposal items" }, { status: 500 });
  }

  const response = {
    id: proposal.id,
    client_email: proposal.client_email,
    client_name: `${proposal.client_name_f} ${proposal.client_name_l}`.trim(),
    client_name_f: proposal.client_name_f,
    client_name_l: proposal.client_name_l,
    client_company: proposal.client_company,
    status: STATUS_MAP[proposal.status] || "Unknown",
    status_id: proposal.status,
    total: proposal.total,
    notes: proposal.notes,
    created_at: proposal.created_at,
    updated_at: proposal.updated_at,
    sent_at: proposal.sent_at,
    signed_at: proposal.signed_at,
    converted_order_id: proposal.converted_order_id,
    items: (proposalItems || []).map(item => {
      const service = item.services as { id: string; name: string } | null;
      return {
        id: item.id,
        service_id: item.service_id,
        service_name: service?.name || null,
        quantity: item.quantity,
        price: item.price,
        created_at: item.created_at,
      };
    }),
  };

  return NextResponse.json(response, { status: 201 });
}
