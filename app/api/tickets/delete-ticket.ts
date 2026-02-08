import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

function isValidUUID(str: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

export async function deleteTicket(id: string) {
  if (!isValidUUID(id)) {
    return NextResponse.json({ error: "Invalid ticket ID format." }, { status: 400 });
  }

  // Check ticket exists and is not already deleted
  const { data: existingTicket, error: fetchError } = await supabase
    .from("tickets")
    .select("id")
    .eq("id", id)
    .is("deleted_at", null)
    .single();

  if (fetchError || !existingTicket) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  // Soft delete: set deleted_at timestamp
  const { error: deleteError } = await supabase
    .from("tickets")
    .update({ 
      deleted_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    })
    .eq("id", id);

  if (deleteError) {
    return NextResponse.json({ error: "Failed to delete ticket" }, { status: 500 });
  }

  return new NextResponse(null, { status: 204 });
}
