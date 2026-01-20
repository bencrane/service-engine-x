import { supabase } from "@/lib/supabase";

interface CreateOrderMessageInput {
  message: string;
  user_id?: string;
  staff_only?: boolean;
  files?: string[];
}

interface OrderMessage {
  id: string;
  order_id: string;
  user_id: string | null;
  message: string;
  staff_only: boolean;
  files: string[];
  created_at: string;
}

interface ValidationErrors {
  [key: string]: string[];
}

export async function createOrderMessage(
  order_id: string,
  input: CreateOrderMessageInput,
  authenticatedUserId: string
): Promise<{ data?: OrderMessage; error?: string; errors?: ValidationErrors; status: number }> {

  // Validate UUID format for order_id
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(order_id)) {
    return { error: "Not Found", status: 404 };
  }

  // Validate required fields
  const errors: ValidationErrors = {};

  if (!input.message || typeof input.message !== "string" || input.message.trim() === "") {
    errors.message = ["The message field is required."];
  }

  if (input.user_id !== undefined && input.user_id !== null) {
    if (typeof input.user_id !== "string" || !uuidRegex.test(input.user_id)) {
      errors.user_id = ["The user_id must be a valid UUID."];
    }
  }

  if (input.staff_only !== undefined && typeof input.staff_only !== "boolean") {
    errors.staff_only = ["The staff_only field must be a boolean."];
  }

  if (input.files !== undefined) {
    if (!Array.isArray(input.files)) {
      errors.files = ["The files field must be an array."];
    } else if (!input.files.every((f) => typeof f === "string")) {
      errors.files = ["All files must be strings."];
    }
  }

  if (Object.keys(errors).length > 0) {
    return {
      error: "The given data was invalid.",
      errors,
      status: 400,
    };
  }

  // Check if order exists and is not soft-deleted
  const { data: order, error: orderError } = await supabase
    .from("orders")
    .select("id")
    .eq("id", order_id)
    .is("deleted_at", null)
    .single();

  if (orderError || !order) {
    return { error: "Not Found", status: 404 };
  }

  // Determine user_id (default to authenticated user)
  const finalUserId = input.user_id || authenticatedUserId;

  // Validate user_id if provided (referential integrity)
  if (input.user_id) {
    const { data: user, error: userError } = await supabase
      .from("users")
      .select("id")
      .eq("id", input.user_id)
      .single();

    if (userError || !user) {
      return {
        error: "The given data was invalid.",
        errors: { user_id: ["The specified user does not exist."] },
        status: 422,
      };
    }
  }

  // Prepare message data
  const messageData = {
    order_id,
    user_id: finalUserId,
    message: input.message.trim(),
    staff_only: input.staff_only ?? false,
    files: input.files ?? [],
  };

  // Insert message
  const { data: newMessage, error: insertError } = await supabase
    .from("order_messages")
    .insert(messageData)
    .select("id, order_id, user_id, message, staff_only, files, created_at")
    .single();

  if (insertError) {
    console.error("Failed to create order message:", insertError);
    return { error: "Internal server error", status: 500 };
  }

  // Update order.last_message_at (required side effect)
  const { error: updateError } = await supabase
    .from("orders")
    .update({
      last_message_at: newMessage.created_at,
      updated_at: new Date().toISOString(),
    })
    .eq("id", order_id);

  if (updateError) {
    console.error("Failed to update order last_message_at:", updateError);
    // Don't fail the request, message was created
  }

  return {
    data: {
      id: newMessage.id,
      order_id: newMessage.order_id,
      user_id: newMessage.user_id,
      message: newMessage.message,
      staff_only: newMessage.staff_only,
      files: newMessage.files || [],
      created_at: newMessage.created_at,
    },
    status: 201,
  };
}
