import { z } from "zod";
import { env } from "./env.js";
import { callSerxApi, type ApiCallResult, type AuthMode, type HttpMethod } from "./http-client.js";
import type { SerxToolError } from "./errors.js";

export type ToolKind = "RO" | "IDEMP" | "MUT" | "DEST";

export interface ToolDefinition {
  name: string;
  kind: ToolKind;
  method: HttpMethod;
  path: string;
  authMode: AuthMode;
  description: string;
  allowBody?: boolean;
  suggestedTools?: string[];
}

export const ToolOutputSchema = {
  ok: z.boolean(),
  status: z.number(),
  data: z.unknown(),
  error: z
    .object({
      category: z.enum(["auth_error", "validation_error", "not_found", "conflict", "upstream_error"]),
      message: z.string(),
      retryable: z.boolean().optional(),
      suggestedTools: z.array(z.string()).optional(),
      status: z.number().optional(),
    })
    .optional(),
};

export function annotationFromKind(kind: ToolKind) {
  if (kind === "RO") {
    return {
      readOnlyHint: true,
      idempotentHint: true,
      destructiveHint: false,
      openWorldHint: true,
    };
  }
  if (kind === "IDEMP") {
    return {
      readOnlyHint: false,
      idempotentHint: true,
      destructiveHint: false,
      openWorldHint: true,
    };
  }
  if (kind === "DEST") {
    return {
      readOnlyHint: false,
      idempotentHint: false,
      destructiveHint: true,
      openWorldHint: true,
    };
  }
  return {
    readOnlyHint: false,
    idempotentHint: false,
    destructiveHint: false,
    openWorldHint: true,
  };
}

const INTERNAL = "internal" as const;
const SERVICE = "service" as const;

export const coreToolDefinitions: ToolDefinition[] = [
  // 5.1 Cal Webhook / normalization
  { name: "serx_create_cal_raw_event", kind: "MUT", method: "POST", path: "/api/internal/cal/events/raw", authMode: INTERNAL, allowBody: true, description: "Stores immutable raw Cal webhook payloads for replay-safe ingestion." },
  { name: "serx_list_unprocessed_cal_raw_events", kind: "RO", method: "GET", path: "/api/internal/cal/events/raw/unprocessed", authMode: INTERNAL, description: "Lists unprocessed raw Cal events in chronological order for queue processing." },
  { name: "serx_mark_cal_raw_event_processed", kind: "IDEMP", method: "PATCH", path: "/api/internal/cal/events/raw/{event_id}/processed", authMode: INTERNAL, allowBody: true, description: "Marks a raw event processed to prevent duplicate orchestration work." },
  { name: "serx_get_cal_raw_event", kind: "RO", method: "GET", path: "/api/internal/cal/raw-events/{event_id}", authMode: INTERNAL, description: "Retrieves a stored raw Cal.com webhook event by ID, including the full payload JSONB." },
  { name: "serx_create_booking_event", kind: "MUT", method: "POST", path: "/api/internal/cal/booking-events", authMode: INTERNAL, allowBody: true, description: "Creates a normalized booking lifecycle event from explicit fields or raw payload." },
  { name: "serx_get_booking_events_by_uid", kind: "RO", method: "GET", path: "/api/internal/cal/booking-events/by-uid/{cal_booking_uid}", authMode: INTERNAL, description: "Gets full booking event history and attendees by Cal booking UID." },
  { name: "serx_get_booking_events_by_booking_id", kind: "RO", method: "GET", path: "/api/internal/cal/booking-events/by-booking-id/{cal_booking_id}", authMode: INTERNAL, description: "Gets normalized booking events by numeric booking ID." },
  { name: "serx_get_latest_booking_event_by_uid", kind: "RO", method: "GET", path: "/api/internal/cal/booking-events/latest/by-uid/{cal_booking_uid}", authMode: INTERNAL, description: "Fetches the latest normalized booking event for a booking UID." },
  { name: "serx_bulk_upsert_booking_attendees", kind: "IDEMP", method: "POST", path: "/api/internal/cal/booking-attendees/bulk", authMode: INTERNAL, allowBody: true, description: "Upserts attendees/hosts using conflict-safe keys for retry-safe participant normalization." },
  { name: "serx_get_booking_attendees_by_uid", kind: "RO", method: "GET", path: "/api/internal/cal/booking-attendees/by-uid/{cal_booking_uid}", authMode: INTERNAL, description: "Lists normalized attendees and hosts by booking UID." },
  { name: "serx_create_or_upsert_recording", kind: "IDEMP", method: "POST", path: "/api/internal/cal/recordings", authMode: INTERNAL, allowBody: true, description: "Creates or updates recording metadata linked to Cal booking identifiers." },
  { name: "serx_get_recordings_by_uid", kind: "RO", method: "GET", path: "/api/internal/cal/recordings/by-uid/{cal_booking_uid}", authMode: INTERNAL, description: "Lists recordings for a Cal booking UID." },
  { name: "serx_update_recording", kind: "IDEMP", method: "PATCH", path: "/api/internal/cal/recordings/{recording_id}", authMode: INTERNAL, allowBody: true, description: "Updates recording enrichment fields like transcript URL and status." },

  // 5.1b Webhook events (serx-webhooks webhook_events_raw read surface)
  { name: "serx_get_webhook_event", kind: "RO", method: "GET", path: "/api/internal/webhook-events/{event_id}", authMode: INTERNAL, description: "Retrieves a stored webhook_events_raw row (full payload + headers) by id. Use with event_ref.id from managed-agents session initial message." },

  // 5.2 Meeting + Deal lifecycle
  { name: "serx_resolve_org_from_event_type", kind: "RO", method: "GET", path: "/api/internal/resolve-org", authMode: INTERNAL, description: "Resolves org/tenant context from Cal event type ID before write operations." },
  { name: "serx_resolve_org_from_team_id", kind: "RO", method: "GET", path: "/api/internal/resolve-org-from-team", authMode: INTERNAL, description: "Resolves org/tenant context directly from a Cal.com team ID without needing an event type." },
  { name: "serx_create_meeting_from_cal_event", kind: "IDEMP", method: "POST", path: "/api/internal/orgs/{org_id}/meetings/from-cal-event", authMode: INTERNAL, allowBody: true, description: "Creates or deduplicates a meeting from Cal event payload context." },
  { name: "serx_update_meeting", kind: "IDEMP", method: "PUT", path: "/api/internal/orgs/{org_id}/meetings/{meeting_id}", authMode: INTERNAL, allowBody: true, description: "Updates internal meeting orchestration fields and linked deal context." },
  { name: "serx_get_meeting_by_cal_uid", kind: "RO", method: "GET", path: "/api/internal/orgs/{org_id}/meetings/by-cal-uid/{cal_event_uid}", authMode: INTERNAL, description: "Retrieves meeting by Cal event UID." },
  { name: "serx_get_meeting_by_cal_booking_id", kind: "RO", method: "GET", path: "/api/internal/orgs/{org_id}/meetings/by-cal-booking-id/{cal_booking_id}", authMode: INTERNAL, description: "Retrieves meeting by numeric Cal booking ID." },
  { name: "serx_create_deal_from_meeting", kind: "MUT", method: "POST", path: "/api/internal/orgs/{org_id}/deals", authMode: INTERNAL, allowBody: true, description: "Creates a qualified deal from a meeting and links it back to meeting context." },
  { name: "serx_get_deal_context", kind: "RO", method: "GET", path: "/api/internal/orgs/{org_id}/deals/{deal_id}", authMode: INTERNAL, description: "Gets rich deal context including account/contact/proposal/meeting joins." },
  { name: "serx_update_deal", kind: "IDEMP", method: "PUT", path: "/api/internal/orgs/{org_id}/deals/{deal_id}", authMode: INTERNAL, allowBody: true, description: "Updates deal state and metadata with lifecycle transition validation." },
  { name: "serx_link_proposal_to_deal", kind: "IDEMP", method: "PUT", path: "/api/internal/orgs/{org_id}/deals/{deal_id}/proposal", authMode: INTERNAL, allowBody: true, description: "Links proposal to deal and advances status to proposal_sent." },

  // 5.3 Internal read/admin support
  { name: "serx_list_orgs", kind: "RO", method: "GET", path: "/api/internal/orgs", authMode: INTERNAL, description: "Lists organizations available to internal automation." },
  { name: "serx_list_org_services_internal", kind: "RO", method: "GET", path: "/api/internal/orgs/{org_id}/services", authMode: INTERNAL, description: "Lists active internal services for an organization." },
  { name: "serx_create_service_internal", kind: "MUT", method: "POST", path: "/api/internal/services", authMode: INTERNAL, allowBody: true, description: "Creates an internal service record for an organization." },
  { name: "serx_create_proposal_internal", kind: "MUT", method: "POST", path: "/api/internal/proposals", authMode: INTERNAL, allowBody: true, description: "Creates and dispatches proposal through internal admin flow." },
  { name: "serx_list_accounts", kind: "RO", method: "GET", path: "/api/internal/orgs/{org_id}/accounts", authMode: INTERNAL, description: "Lists org accounts with optional text search." },
  { name: "serx_get_account", kind: "RO", method: "GET", path: "/api/internal/orgs/{org_id}/accounts/{account_id}", authMode: INTERNAL, description: "Gets an account by ID in org scope." },
  { name: "serx_list_contacts", kind: "RO", method: "GET", path: "/api/internal/orgs/{org_id}/contacts", authMode: INTERNAL, description: "Lists org contacts with optional search/account filtering." },
  { name: "serx_get_contact", kind: "RO", method: "GET", path: "/api/internal/orgs/{org_id}/contacts/{contact_id}", authMode: INTERNAL, description: "Gets a contact by ID in org scope." },
  { name: "serx_upsert_contact", kind: "IDEMP", method: "POST", path: "/api/internal/orgs/{org_id}/contacts/upsert", authMode: INTERNAL, allowBody: true, description: "Upserts a contact by (org_id, email). Returns {contact_id, created}. Used by Cal.com booking orchestration to ensure attendee contacts exist." },
  { name: "serx_list_proposals_internal", kind: "RO", method: "GET", path: "/api/internal/orgs/{org_id}/proposals", authMode: INTERNAL, description: "Lists org proposals from internal API surface." },
  { name: "serx_get_proposal_internal", kind: "RO", method: "GET", path: "/api/internal/orgs/{org_id}/proposals/{proposal_id}", authMode: INTERNAL, description: "Gets a proposal by ID from internal API surface." },
  { name: "serx_get_proposal_deliverables", kind: "RO", method: "GET", path: "/api/internal/orgs/{org_id}/proposals/{proposal_id}/deliverables", authMode: INTERNAL, description: "Gets signed proposal deliverables, engagement, and project context." },
  { name: "serx_list_engagements", kind: "RO", method: "GET", path: "/api/internal/orgs/{org_id}/engagements", authMode: INTERNAL, description: "Lists engagements with account and project summary context." },
  { name: "serx_get_engagement", kind: "RO", method: "GET", path: "/api/internal/orgs/{org_id}/engagements/{engagement_id}", authMode: INTERNAL, description: "Gets detailed engagement including linked projects and services." },
  { name: "serx_list_projects", kind: "RO", method: "GET", path: "/api/internal/orgs/{org_id}/projects", authMode: INTERNAL, description: "Lists projects for org with status and engagement filters." },
  { name: "serx_get_project", kind: "RO", method: "GET", path: "/api/internal/orgs/{org_id}/projects/{project_id}", authMode: INTERNAL, description: "Gets detailed project including service and engagement context." },
  { name: "serx_list_orders_internal", kind: "RO", method: "GET", path: "/api/internal/orgs/{org_id}/orders", authMode: INTERNAL, description: "Lists internal orders for org with status/account filtering." },
  { name: "serx_get_order_internal", kind: "RO", method: "GET", path: "/api/internal/orgs/{org_id}/orders/{order_id}", authMode: INTERNAL, description: "Gets an internal order by ID in org scope." },

  // 5.4 OpenAPI-covered Next routes
  { name: "serx_health_check", kind: "RO", method: "GET", path: "/api/health", authMode: SERVICE, description: "Runs API health check before workflow execution." },
  { name: "serx_list_clients", kind: "RO", method: "GET", path: "/api/clients", authMode: SERVICE, description: "Lists clients with pagination and filters." },
  { name: "serx_create_client", kind: "MUT", method: "POST", path: "/api/clients", authMode: SERVICE, allowBody: true, description: "Creates a new client record." },
  { name: "serx_get_client", kind: "RO", method: "GET", path: "/api/clients/{client_id}", authMode: SERVICE, description: "Gets a client by identifier." },
  { name: "serx_update_client", kind: "MUT", method: "PUT", path: "/api/clients/{client_id}", authMode: SERVICE, allowBody: true, description: "Updates mutable client fields." },
  { name: "serx_delete_client", kind: "DEST", method: "DELETE", path: "/api/clients/{client_id}", authMode: SERVICE, description: "Deletes/deactivates a client record." },
  { name: "serx_list_services", kind: "RO", method: "GET", path: "/api/services", authMode: SERVICE, description: "Lists services from public API layer." },
  { name: "serx_create_service", kind: "MUT", method: "POST", path: "/api/services", authMode: SERVICE, allowBody: true, description: "Creates a service from public API layer." },
  { name: "serx_get_service", kind: "RO", method: "GET", path: "/api/services/{service_id}", authMode: SERVICE, description: "Gets a service by ID." },
  { name: "serx_update_service", kind: "MUT", method: "PUT", path: "/api/services/{service_id}", authMode: SERVICE, allowBody: true, description: "Updates service details." },
  { name: "serx_delete_service", kind: "DEST", method: "DELETE", path: "/api/services/{service_id}", authMode: SERVICE, description: "Deletes/deactivates a service." },
  { name: "serx_list_order_messages", kind: "RO", method: "GET", path: "/api/orders/{order_id}/messages", authMode: SERVICE, description: "Lists message thread for an order." },
  { name: "serx_create_order_message", kind: "MUT", method: "POST", path: "/api/orders/{order_id}/messages", authMode: SERVICE, allowBody: true, description: "Creates message entry in an order thread." },
  { name: "serx_delete_order_message", kind: "DEST", method: "DELETE", path: "/api/order-messages/{order_message_id}", authMode: SERVICE, description: "Deletes an order message." },
  { name: "serx_list_order_tasks", kind: "RO", method: "GET", path: "/api/orders/{order_id}/tasks", authMode: SERVICE, description: "Lists tasks under an order." },
  { name: "serx_create_order_task", kind: "MUT", method: "POST", path: "/api/orders/{order_id}/tasks", authMode: SERVICE, allowBody: true, description: "Creates an order task." },
  { name: "serx_update_order_task", kind: "MUT", method: "PUT", path: "/api/order-tasks/{task_id}", authMode: SERVICE, allowBody: true, description: "Updates an existing order task." },
  { name: "serx_delete_order_task", kind: "DEST", method: "DELETE", path: "/api/order-tasks/{task_id}", authMode: SERVICE, description: "Deletes an order task." },
  { name: "serx_list_proposals", kind: "RO", method: "GET", path: "/api/proposals", authMode: SERVICE, description: "Lists proposals from public API layer." },
  { name: "serx_get_proposal", kind: "RO", method: "GET", path: "/api/proposals/{proposal_id}", authMode: SERVICE, description: "Gets proposal details by ID." },
  { name: "serx_create_proposal", kind: "MUT", method: "POST", path: "/api/proposals", authMode: SERVICE, allowBody: true, description: "Creates proposal from public API layer." },
  { name: "serx_send_proposal", kind: "MUT", method: "PATCH", path: "/api/proposals/{proposal_id}/send", authMode: SERVICE, allowBody: true, description: "Marks draft proposal as sent." },
  { name: "serx_sign_proposal", kind: "MUT", method: "PATCH", path: "/api/proposals/{proposal_id}/sign", authMode: SERVICE, allowBody: true, description: "Signs proposal and triggers conversion path." },

  // 5.5 Next route-only coverage
  { name: "serx_list_orders", kind: "RO", method: "GET", path: "/api/orders", authMode: SERVICE, description: "Lists orders from Next API implementation." },
  { name: "serx_create_order", kind: "MUT", method: "POST", path: "/api/orders", authMode: SERVICE, allowBody: true, description: "Creates a new order." },
  { name: "serx_get_order", kind: "RO", method: "GET", path: "/api/orders/{order_id}", authMode: SERVICE, description: "Gets an order by ID." },
  { name: "serx_update_order", kind: "MUT", method: "PUT", path: "/api/orders/{order_id}", authMode: SERVICE, allowBody: true, description: "Updates mutable order fields." },
  { name: "serx_delete_order", kind: "DEST", method: "DELETE", path: "/api/orders/{order_id}", authMode: SERVICE, description: "Deletes/deactivates an order." },
  { name: "serx_mark_order_task_complete", kind: "MUT", method: "POST", path: "/api/order-tasks/{task_id}/complete", authMode: SERVICE, allowBody: true, description: "Marks an order task complete via dedicated completion route." },
  { name: "serx_mark_order_task_incomplete", kind: "MUT", method: "DELETE", path: "/api/order-tasks/{task_id}/complete", authMode: SERVICE, description: "Reverts an order task to incomplete state." },
  { name: "serx_list_invoices", kind: "RO", method: "GET", path: "/api/invoices", authMode: SERVICE, description: "Lists invoices for billing workflows." },
  { name: "serx_create_invoice", kind: "MUT", method: "POST", path: "/api/invoices", authMode: SERVICE, allowBody: true, description: "Creates an invoice." },
  { name: "serx_get_invoice", kind: "RO", method: "GET", path: "/api/invoices/{invoice_id}", authMode: SERVICE, description: "Gets an invoice by ID." },
  { name: "serx_update_invoice", kind: "MUT", method: "PUT", path: "/api/invoices/{invoice_id}", authMode: SERVICE, allowBody: true, description: "Updates mutable invoice fields." },
  { name: "serx_delete_invoice", kind: "DEST", method: "DELETE", path: "/api/invoices/{invoice_id}", authMode: SERVICE, description: "Deletes/deactivates an invoice." },
  { name: "serx_charge_invoice", kind: "MUT", method: "POST", path: "/api/invoices/{invoice_id}/charge", authMode: SERVICE, allowBody: true, description: "Charges invoice through configured payment rails." },
  { name: "serx_mark_invoice_paid", kind: "MUT", method: "POST", path: "/api/invoices/{invoice_id}/mark_paid", authMode: SERVICE, allowBody: true, description: "Marks invoice paid for out-of-band settlements." },
  { name: "serx_list_tickets", kind: "RO", method: "GET", path: "/api/tickets", authMode: SERVICE, description: "Lists support tickets." },
  { name: "serx_create_ticket", kind: "MUT", method: "POST", path: "/api/tickets", authMode: SERVICE, allowBody: true, description: "Creates support ticket." },
  { name: "serx_get_ticket", kind: "RO", method: "GET", path: "/api/tickets/{ticket_id}", authMode: SERVICE, description: "Gets a support ticket by ID." },
  { name: "serx_update_ticket", kind: "MUT", method: "PUT", path: "/api/tickets/{ticket_id}", authMode: SERVICE, allowBody: true, description: "Updates ticket fields and status." },
  { name: "serx_delete_ticket", kind: "DEST", method: "DELETE", path: "/api/tickets/{ticket_id}", authMode: SERVICE, description: "Deletes/deactivates ticket." },
];

function extractPathTokens(path: string): string[] {
  const matches = path.match(/\{([^}]+)\}/g) ?? [];
  return matches.map((match) => match.slice(1, -1));
}

function makeInputSchema(def: ToolDefinition) {
  const tokens = extractPathTokens(def.path);
  const shape: Record<string, z.ZodTypeAny> = {
    query: z.record(z.unknown()).optional().describe("Optional query parameters forwarded to upstream endpoint."),
    body: z.unknown().optional().describe("Optional request body forwarded to upstream endpoint."),
  };

  for (const token of tokens) {
    shape[token] = z.union([z.string().min(1), z.number()]).describe(`Path parameter: ${token}`);
  }

  return z.object(shape).passthrough();
}

function applyPathParams(path: string, input: Record<string, unknown>): string {
  let nextPath = path;
  for (const token of extractPathTokens(path)) {
    const value = input[token];
    if (value === undefined || value === null || value === "") {
      throw new Error(`Missing required path parameter '${token}'.`);
    }
    nextPath = nextPath.replace(`{${token}}`, encodeURIComponent(String(value)));
  }
  return nextPath;
}

function splitPayload(def: ToolDefinition, input: Record<string, unknown>) {
  const tokens = new Set(extractPathTokens(def.path));
  const query = (input.query as Record<string, unknown> | undefined) ?? {};
  let body = input.body;

  if (def.allowBody && body === undefined) {
    const fallbackBody: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(input)) {
      if (key === "query" || key === "body" || tokens.has(key)) continue;
      fallbackBody[key] = value;
    }
    if (Object.keys(fallbackBody).length > 0) {
      body = fallbackBody;
    }
  }

  return {
    query,
    body,
  };
}

export function isDestructiveBlocked(def: ToolDefinition): boolean {
  return def.kind === "DEST" && !env.allowDestructiveTools;
}

export async function executeCoreTool(def: ToolDefinition, input: Record<string, unknown>): Promise<ApiCallResult> {
  if (isDestructiveBlocked(def)) {
    const destructiveBlockedError: SerxToolError = {
      category: "validation_error",
      message:
        "Destructive tools are disabled. Set SERX_ALLOW_DESTRUCTIVE_TOOLS=true for an explicit controlled run.",
      retryable: false,
      status: 403,
    };
    return {
      ok: false,
      status: 403,
      data: null,
      error: destructiveBlockedError,
    };
  }

  const path = applyPathParams(def.path, input);
  const payload = splitPayload(def, input);
  const result = await callSerxApi({
    toolName: def.name,
    method: def.method,
    path,
    authMode: def.authMode,
    query: payload.query,
    body: payload.body,
  });

  if (!result.ok && result.error) {
    result.error.suggestedTools = result.error.suggestedTools ?? def.suggestedTools;
  }

  return result;
}

export function getToolInputSchema(def: ToolDefinition) {
  return makeInputSchema(def);
}
