import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

function isValidUUID(str: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

export async function deleteOrder(id: string, orgId: string) {
  if (!isValidUUID(id)) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  // Check order exists and is not already deleted
  const { data: existingOrder, error: fetchError } = await supabase
    .from("orders")
    .select("id")
    .eq("id", id)
    .eq("org_id", orgId)
    .is("deleted_at", null)
    .single();

  if (fetchError || !existingOrder) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  // Soft delete: set deleted_at timestamp
  const { error: deleteError } = await supabase
    .from("orders")
    .update({ deleted_at: new Date().toISOString() })
    .eq("id", id);

  if (deleteError) {
    return NextResponse.json({ error: "Failed to delete order" }, { status: 500 });
  }

  return new NextResponse(null, { status: 204 });
}
