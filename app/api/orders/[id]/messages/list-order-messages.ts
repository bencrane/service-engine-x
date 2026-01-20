import { supabase } from "@/lib/supabase";

interface ListOrderMessagesParams {
  order_id: string;
  limit?: number;
  page?: number;
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

interface PaginatedResponse {
  data: OrderMessage[];
  links: {
    first: string;
    last: string;
    prev: string | null;
    next: string | null;
  };
  meta: {
    current_page: number;
    from: number;
    to: number;
    last_page: number;
    per_page: number;
    total: number;
    path: string;
  };
}

export async function listOrderMessages(
  params: ListOrderMessagesParams,
  baseUrl: string
): Promise<{ data?: PaginatedResponse; error?: string; status: number }> {

  const { order_id, limit = 20, page = 1 } = params;

  // Validate UUID format
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(order_id)) {
    return { error: "Not Found", status: 404 };
  }

  // Validate pagination params
  const validLimit = Math.max(1, Math.min(100, limit));
  const validPage = Math.max(1, page);
  const offset = (validPage - 1) * validLimit;

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

  // Get total count
  const { count, error: countError } = await supabase
    .from("order_messages")
    .select("*", { count: "exact", head: true })
    .eq("order_id", order_id);

  if (countError) {
    return { error: "Internal server error", status: 500 };
  }

  const total = count || 0;
  const lastPage = Math.ceil(total / validLimit) || 1;

  // Get messages (sorted by created_at descending)
  const { data: messages, error: messagesError } = await supabase
    .from("order_messages")
    .select("id, order_id, user_id, message, staff_only, files, created_at")
    .eq("order_id", order_id)
    .order("created_at", { ascending: false })
    .range(offset, offset + validLimit - 1);

  if (messagesError) {
    return { error: "Internal server error", status: 500 };
  }

  const path = `${baseUrl}/api/orders/${order_id}/messages`;

  const response: PaginatedResponse = {
    data: (messages || []).map((m) => ({
      id: m.id,
      order_id: m.order_id,
      user_id: m.user_id,
      message: m.message,
      staff_only: m.staff_only,
      files: m.files || [],
      created_at: m.created_at,
    })),
    links: {
      first: `${path}?page=1&limit=${validLimit}`,
      last: `${path}?page=${lastPage}&limit=${validLimit}`,
      prev: validPage > 1 ? `${path}?page=${validPage - 1}&limit=${validLimit}` : null,
      next: validPage < lastPage ? `${path}?page=${validPage + 1}&limit=${validLimit}` : null,
    },
    meta: {
      current_page: validPage,
      from: total > 0 ? offset + 1 : 0,
      to: Math.min(offset + validLimit, total),
      last_page: lastPage,
      per_page: validLimit,
      total,
      path,
    },
  };

  return { data: response, status: 200 };
}
