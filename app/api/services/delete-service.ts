import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

function isValidUUID(str: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

export async function deleteService(id: string, orgId: string) {
  if (!isValidUUID(id)) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  const { data: existingService, error: fetchError } = await supabase
    .from("services")
    .select("id")
    .eq("id", id)
    .eq("org_id", orgId)
    .is("deleted_at", null)
    .single();

  if (fetchError || !existingService) {
    return NextResponse.json({ error: "Not Found" }, { status: 404 });
  }

  // Soft delete: set deleted_at timestamp
  const { error: deleteError } = await supabase
    .from("services")
    .update({ deleted_at: new Date().toISOString() })
    .eq("id", id);

  if (deleteError) {
    return NextResponse.json({ error: "Failed to delete service" }, { status: 500 });
  }

  return new NextResponse(null, { status: 204 });
}
