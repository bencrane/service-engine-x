import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

function isValidUUID(str: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

export async function deleteClient(id: string, orgId: string) {
  if (!isValidUUID(id)) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  const { data: clientRole } = await supabase
    .from("roles")
    .select("id")
    .eq("dashboard_access", 0)
    .single();

  if (!clientRole) {
    return NextResponse.json({ error: "Client role not configured" }, { status: 500 });
  }

  const { data: existingClient, error: fetchError } = await supabase
    .from("users")
    .select("id")
    .eq("id", id)
    .eq("org_id", orgId)
    .eq("role_id", clientRole.id)
    .single();

  if (fetchError || !existingClient) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  // FK guard: check for dependent records
  const { data: orders } = await supabase
    .from("orders")
    .select("id")
    .eq("user_id", id)
    .limit(1);

  if (orders && orders.length > 0) {
    return NextResponse.json(
      { error: "Cannot delete client with existing orders" },
      { status: 409 }
    );
  }

  const { data: invoices } = await supabase
    .from("invoices")
    .select("id")
    .eq("user_id", id)
    .limit(1);

  if (invoices && invoices.length > 0) {
    return NextResponse.json(
      { error: "Cannot delete client with existing invoices" },
      { status: 409 }
    );
  }

  const { data: tickets } = await supabase
    .from("tickets")
    .select("id")
    .eq("user_id", id)
    .limit(1);

  if (tickets && tickets.length > 0) {
    return NextResponse.json(
      { error: "Cannot delete client with existing tickets" },
      { status: 409 }
    );
  }

  const { data: subscriptions } = await supabase
    .from("subscriptions")
    .select("id")
    .eq("user_id", id)
    .limit(1);

  if (subscriptions && subscriptions.length > 0) {
    return NextResponse.json(
      { error: "Cannot delete client with existing subscriptions" },
      { status: 409 }
    );
  }

  // Hard delete
  const { error: deleteError } = await supabase
    .from("users")
    .delete()
    .eq("id", id);

  if (deleteError) {
    return NextResponse.json({ error: "Failed to delete client" }, { status: 500 });
  }

  return new NextResponse(null, { status: 204 });
}
