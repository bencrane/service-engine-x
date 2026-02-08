import { supabase } from "@/lib/supabase";

export async function deleteInvoice(
  id: string,
  orgId: string
): Promise<{ error?: string; status: number }> {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(id)) {
    return { error: "Not Found", status: 404 };
  }

  // Check if invoice exists and is not already deleted
  const { data: invoice, error: fetchError } = await supabase
    .from("invoices")
    .select("id, deleted_at")
    .eq("id", id)
    .eq("org_id", orgId)
    .single();

  if (fetchError || !invoice) {
    return { error: "Not Found", status: 404 };
  }

  if (invoice.deleted_at) {
    return { error: "Not Found", status: 404 };
  }

  // Soft delete
  const { error: updateError } = await supabase
    .from("invoices")
    .update({ deleted_at: new Date().toISOString() })
    .eq("id", id);

  if (updateError) {
    console.error("Failed to delete invoice:", updateError);
    return { error: "Internal server error", status: 500 };
  }

  return { status: 204 };
}
