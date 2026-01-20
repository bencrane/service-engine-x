import { supabase } from "@/lib/supabase";

export async function deleteOrderMessage(
  id: string
): Promise<{ error?: string; status: number }> {

  // Validate UUID format
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(id)) {
    return { error: "Not Found", status: 404 };
  }

  // Check if message exists
  const { data: message, error: fetchError } = await supabase
    .from("order_messages")
    .select("id")
    .eq("id", id)
    .single();

  if (fetchError || !message) {
    return { error: "Not Found", status: 404 };
  }

  // Hard delete the message
  const { error: deleteError } = await supabase
    .from("order_messages")
    .delete()
    .eq("id", id);

  if (deleteError) {
    console.error("Failed to delete order message:", deleteError);
    return { error: "Internal server error", status: 500 };
  }

  // Note: We intentionally do NOT recalculate orders.last_message_at
  // as documented - this would be expensive and the field indicates
  // activity timing, not current message count

  return { status: 204 };
}
