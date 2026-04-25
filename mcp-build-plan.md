# MCP Build Plan for Service-Engine-X

## 0) System Context (Authoritative)

This MCP server exists to support a multi-agent architecture powered by Claude Managed Agents, with **service-engine-x as the only system of record** for this workflow.

- **Intake agent** receives Cal.com webhooks, stores raw payloads, classifies event type (`BOOKING_CREATED`, `BOOKING_CANCELLED`, `BOOKING_RESCHEDULED`, `MEETING_ENDED`), and routes execution.
- **Four functional orchestrator agents** (one per event type) coordinate specialized sub-agents for downstream actions (proposal flows, sales context, CRM updates, follow-up actions).
- **Service-engine-x MCP server** is the single integration layer between Managed Agent sessions and engine-x APIs.
- All event processing, normalization, meeting/deal lifecycle transitions, and persistence run through **service-engine-x internal endpoints** backed by **service-engine-x Supabase**.

### Deprecated/Archived Systems (Explicitly Excluded)

- Modal serverless ingestion codepaths (including `calcom_ingest.py`) are **deprecated, archived, and out of scope**.
- Any Outbound Supabase or secondary-database architecture is **deprecated, archived, and no longer relevant**.
- This plan does not depend on, integrate with, or reference those deprecated runtime paths for implementation decisions.

## Objective

Build a production-grade TypeScript MCP server for Claude Managed Agents that can orchestrate the Cal.com booking/deal lifecycle while also exposing broad Service-Engine-X API coverage. The design favors atomic, composable tools with consistent `serx_` namespacing and actionable error guidance. Compound workflow tools are included selectively where they reduce orchestration fragility without hiding core primitives.

## Source-of-Truth Inputs Reviewed

- `service-engine-x-api-docs/PROJECT-GUIDE.md`
- `service-engine-x-api/docs/CALCOM-DEALS.md` (requested `reference-docs/cal-booking-deal-logic.md` equivalent was not present)
- `mcp-tools-guide.md` (requested `reference-docs/mcp-tools-guide.md` equivalent was not present)
- `~/.claude/skills/mcp-builder/SKILL.md`
- `~/.claude/skills/mcp-builder/reference/node_mcp_server.md`
- `~/.claude/skills/mcp-builder/reference/mcp_best_practices.md`
- `~/.claude/skills/mcp-builder/reference/evaluation.md`
- All files under `openapi/routes/`
- All files under `app/api/`
- `lib/auth.ts`
- `lib/supabase.ts`
- Cal/deal internal routers in `service-engine-x-api/app/routers/` (`internal_cal_events.py`, `internal_meetings_deals.py`, `internal.py`) to cover `x-internal-key` lifecycle operations explicitly required by the pipeline.
- Historical Modal/Outbound artifacts were treated as deprecated/archived context and excluded from architecture assumptions.

---

## 1) Architecture Decision: Where MCP Server Lives

### Options Evaluated

1. **New service in Railway (recommended)**  
2. **Next.js API route (`/api/mcp`) inside current app**  
3. **Standalone entrypoint in same repo (single process, manually hosted)**

### Recommendation: Dedicated Railway service (`service-engine-x-mcp`)

Use a new TypeScript service in this monorepo, deployed as a separate Railway service, using MCP SDK Streamable HTTP transport.

### Why this is best

- **Operational isolation:** MCP request patterns (long-running, tool-heavy, bursty) differ from user-facing API traffic; separate scaling and failure domains are cleaner.
- **Security boundary clarity:** Managed-agent auth, internal-key forwarding, and allowlists can be implemented in a single MCP gateway layer without coupling to web app auth middleware.
- **Protocol fit:** Streamable HTTP transport is first-class for remote MCP; avoids bolting MCP protocol semantics onto Next route handlers.
- **Deployment simplicity:** Railway already hosts related services; add one service with Doppler-managed secrets and a dedicated public MCP URL.

### Tradeoffs

- **Extra service overhead:** Another deploy unit, health checks, and observability surface area.
- **Cross-service latency:** MCP service calls into internal APIs over network hops.
- **Schema drift risk:** Needs explicit sync process from OpenAPI metadata to MCP tool schemas.

### Why not `/api/mcp` in Next.js

- Shared runtime and middleware complexity increases blast radius.
- Harder to tune MCP-specific throughput/timeouts independently.
- Conflates public API concerns and agent-orchestration concerns.

---

## 2) Transport + Deployment + URL + Environment Flow

### Transport

- **Primary:** Streamable HTTP (`POST /mcp`) with stateless request handling.
- **Avoid:** SSE (deprecated for new MCP designs).

### Railway deployment model

- New service: `service-engine-x-mcp`
- Build target: Node 20+, TypeScript compile to `dist/`
- Health endpoint: `/healthz` (non-MCP)
- MCP endpoint: `/mcp`

### Public URL pattern

- `https://serx-mcp.<railway-domain>/mcp` (or custom domain `https://mcp.serviceengine.xyz/mcp`)
- HTTPS required end-to-end (Managed Agents connector requirement + secret transit safety).

### Doppler/env variable flow

- Doppler project config injects:
  - `SERX_MCP_AUTH_TOKEN` (inbound auth from Managed Agents)
  - `SERX_INTERNAL_API_BASE_URL` (internal API target)
  - `SERX_INTERNAL_API_KEY` (for `x-internal-key` calls)
  - `SERX_SERVICE_API_TOKEN` (for Next.js routes protected by bearer token auth)
  - `SERVICE_ENGINE_X_SUPABASE_URL`
  - `SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY`
  - `CAL_API_KEY` (if MCP calls Cal APIs directly; otherwise not required)
- No secrets embedded in tool outputs or logs.

---

## 3) Auth Design

## 3.1 Inbound auth (Managed Agent session -> MCP)

- Use a bearer secret header for MCP server access:
  - `Authorization: Bearer <SERX_MCP_AUTH_TOKEN>`
- Reject unauthenticated calls with actionable text:
  - `"Unauthorized MCP request. Configure Managed Agent connector header Authorization: Bearer <vault secret>."`
- Optional hardening:
  - IP allowlist for Anthropic egress (if available)
  - request-id signing window or HMAC nonce for replay resistance

## 3.2 Egress auth (MCP -> Service-Engine-X internal endpoints)

- For FastAPI internal routes (`/api/internal/*`, `/api/internal/cal/*`), send:
  - `x-internal-key: <SERX_INTERNAL_API_KEY>`
- For Next API routes using bearer token validation (`validateApiToken`), use dedicated service API token:
  - `Authorization: Bearer <SERX_SERVICE_API_TOKEN>`
- Keep these separate to avoid over-privileged single credentials.

## 3.3 Vault mapping (Managed Agents)

- Vault secret keys suggested:
  - `SERX_MCP_BEARER`
  - `SERX_INTERNAL_KEY` (only if connector supports downstream header injection through MCP server env; otherwise only MCP service needs this)
- Managed Agent only needs MCP ingress secret; downstream keys remain server-side in Doppler.

---

## 4) Tool Design Principles for This Server

- Prefix all tools with `serx_`.
- Prefer atomic endpoint-wrapping tools for full API coverage.
- Add a small set of explicitly named compound tools for booking lifecycle orchestration where sequence errors are common.
- Return compact structured data: IDs, statuses, links, key timestamps, and next actions.
- Every error message includes recovery hints (missing org mapping, duplicate meeting, invalid status transition, etc.).
- Every tool defines `outputSchema` and returns both `content` (human-readable) and `structuredContent` (machine-parseable).
- All list/read tools expose explicit pagination controls (`limit`, cursor/page, sort where supported) with conservative defaults.

### 4.1 Tool annotation and idempotency policy (enforced)

- Do not mark create operations as idempotent unless the upstream endpoint enforces a stable idempotency key or deterministic upsert key.
- Tool metadata defaults:
  - True reads (`GET` only): `readOnlyHint=true`, `idempotentHint=true`, `destructiveHint=false`
  - Mutations without idempotency guarantees: `idempotentHint=false`
  - Destructive operations: `destructiveHint=true` and explicit allowlist gate in runtime config
- Initial correction pass for this plan:
  - `serx_create_client`, `serx_create_service`, `serx_create_order`, `serx_create_invoice`, `serx_create_ticket`, `serx_create_proposal` should default to non-idempotent until endpoint-level idempotency keys are added.

---

## 5) Complete MCP Tool Inventory

Notes:
- **Kind:** `RO` (read-only), `IDEMP` (idempotent mutation), `MUT` (non-idempotent mutation), `DEST` (destructive).
- `Wraps` references existing endpoints/handlers.
- Description text is intentionally verbose to meet MCP discoverability guidance.

### 5.1 Cal Webhook Raw Events + Booking Normalization

| Tool | Kind | Description | Input schema summary | Wraps |
|---|---|---|---|---|
| `serx_create_cal_raw_event` | MUT | Stores a raw Cal webhook payload as an immutable audit event so downstream processing can be replayed safely. This tool is used at the start of ingestion to guarantee traceability before any business mutations occur. It returns the raw event identifier and normalized metadata so agents can chain subsequent tools deterministically. | `trigger_event` (string), `payload` (object), optional `org_id`, optional `cal_booking_uid` | `POST /api/internal/cal/events/raw` |
| `serx_list_unprocessed_cal_raw_events` | RO | Fetches raw webhook records that have not been marked processed, ordered by receive time to preserve event chronology. This tool supports batch workers and retry loops while keeping the queue bounded with limit controls. Returned records are compact and include only fields required for routing decisions. | `limit` (1-500, default bounded) | `GET /api/internal/cal/events/raw/unprocessed` |
| `serx_mark_cal_raw_event_processed` | IDEMP | Marks a raw event as processed after successful orchestration completion. This tool prevents duplicate work and enables at-least-once delivery handling without data loss. It accepts an optional timestamp for backfill workflows and returns the updated event state. | `event_id` (uuid), optional `processed_at` | `PATCH /api/internal/cal/events/raw/{event_id}/processed` |
| `serx_create_booking_event` | MUT | Creates a normalized booking lifecycle event from either explicit fields or raw payload-derived fields. This tool enforces supported Cal trigger types and captures organizer, timing, and guest metadata in a consistent format. It also returns related attendees to reduce immediate follow-up read calls. | optional explicit event fields, optional `raw_payload`; requires resolvable `trigger_event` | `POST /api/internal/cal/booking-events` |
| `serx_get_booking_events_by_uid` | RO | Retrieves the full event history and attendees for a Cal booking UID. This tool is used to reconstruct lifecycle progression and verify ordering during retries or incident investigation. The response intentionally includes both event and attendee sets for high-signal context in one call. | `cal_booking_uid` (string) | `GET /api/internal/cal/booking-events/by-uid/{cal_booking_uid}` |
| `serx_get_booking_events_by_booking_id` | RO | Fetches all normalized events for a numeric Cal booking ID where UID may be unavailable or changed after reschedule. This tool helps reconcile webhook payload variants across Cal event payload shapes. It returns events sorted by creation timestamp for deterministic agent reasoning. | `cal_booking_id` (int) | `GET /api/internal/cal/booking-events/by-booking-id/{cal_booking_id}` |
| `serx_get_latest_booking_event_by_uid` | RO | Returns the most recent normalized event for a booking UID to quickly determine current lifecycle state. This tool reduces context load compared with pulling full history when only latest state is needed. It raises a clear not-found error if no event exists for the UID. | `cal_booking_uid` (string) | `GET /api/internal/cal/booking-events/latest/by-uid/{cal_booking_uid}` |
| `serx_bulk_upsert_booking_attendees` | IDEMP | Upserts attendees and hosts for a booking using a conflict key that prevents duplicate participant rows. This tool can derive attendees from raw payload when explicit attendee objects are absent. It returns count and normalized attendee objects so orchestration can proceed without an immediate read-back. | either `attendees[]` or `raw_payload`; optional `booking_event_id`, `org_id` | `POST /api/internal/cal/booking-attendees/bulk` |
| `serx_get_booking_attendees_by_uid` | RO | Retrieves attendee and host records for a booking UID in role/email order. This tool is useful for routing logic, participant enrichment, and no-show attribution workflows. Returned records are normalized and suitable for deterministic downstream comparisons. | `cal_booking_uid` (string) | `GET /api/internal/cal/booking-attendees/by-uid/{cal_booking_uid}` |
| `serx_create_or_upsert_recording` | IDEMP | Creates or updates a recording record for a booking from explicit fields or payload-derived values. This tool ensures recording metadata remains linked to Cal identifiers and supports eventual transcript updates. It returns the persisted canonical recording object for immediate chaining. | recording fields or `raw_payload`; requires `cal_recording_id` resolvable | `POST /api/internal/cal/recordings` |
| `serx_get_recordings_by_uid` | RO | Lists recordings attached to a booking UID for post-meeting workflows and QA checks. This tool keeps response payload focused to recording entities only and sorted by creation time. It is typically used before transcript extraction or sharing workflows. | `cal_booking_uid` (string) | `GET /api/internal/cal/recordings/by-uid/{cal_booking_uid}` |
| `serx_update_recording` | IDEMP | Applies targeted recording field updates such as status, transcript URL, and download link. This tool is intended for asynchronous enrichment steps after recording processors complete. It returns the updated object and clear not-found feedback if the recording ID is invalid. | `recording_id` (uuid), optional `status`, `transcript_url`, `download_link` | `PATCH /api/internal/cal/recordings/{recording_id}` |

### 5.2 Meeting + Deal Lifecycle (Internal)

| Tool | Kind | Description | Input schema summary | Wraps |
|---|---|---|---|---|
| `serx_resolve_org_from_event_type` | RO | Resolves organization context from a Cal event type with cache support. This tool is the required entry point for mapping incoming Cal events to tenant/org scope before any write operations. It returns org identity, team mapping, and cache provenance for auditability. | `event_type_id` (int >=1) | `GET /api/internal/resolve-org` |
| `serx_create_meeting_from_cal_event` | IDEMP | Creates or deduplicates a meeting from Cal booking context and auto-associates account/contact records as needed. This tool handles reschedule transitions and returns both meeting and relationship context needed for deal decisions. It is safe to retry because existing records are returned rather than duplicated when identifiers already exist. | `org_id`, meeting payload (`attendees`, `title`, `start_time`, `end_time`, optional `cal_event_uid`, `cal_booking_id`, `rescheduled_from_uid`) | `POST /api/internal/orgs/{org_id}/meetings/from-cal-event` |
| `serx_update_meeting` | IDEMP | Updates meeting orchestration fields such as status, deal linkage, notes, and recording metadata. This tool enforces status validity and linked-deal existence to prevent inconsistent lifecycle transitions. It returns the updated meeting state suitable for follow-on decision tools. | `org_id`, `meeting_id`, optional status/deal_id/notes/recording/transcript/no-show flags | `PUT /api/internal/orgs/{org_id}/meetings/{meeting_id}` |
| `serx_get_meeting_by_cal_uid` | RO | Fetches one meeting by Cal event UID for fast lookup in webhook handling and replay scenarios. This tool is optimized for deterministic reconciliation when UID is the only stable external key. It returns a not-found error with actionable guidance when upstream create steps were skipped. | `org_id`, `cal_event_uid` | `GET /api/internal/orgs/{org_id}/meetings/by-cal-uid/{cal_event_uid}` |
| `serx_get_meeting_by_cal_booking_id` | RO | Fetches one meeting by numeric Cal booking ID for cases where UID has changed due to rescheduling. This tool supports fallback correlation logic when webhook payloads vary by event type. It returns the canonical meeting object for downstream updates. | `org_id`, `cal_booking_id` (int) | `GET /api/internal/orgs/{org_id}/meetings/by-cal-booking-id/{cal_booking_id}` |
| `serx_create_deal_from_meeting` | MUT | Creates a deal from a qualified meeting and links that deal back onto the meeting atomically from the orchestration perspective. This tool prevents duplicate linkage by rejecting meetings already connected to a deal. It returns both deal and updated meeting context to reduce follow-up read calls. | `org_id`, `meeting_id`, `title`, optional `value`, `source`, `notes`, `referred_by_account_id` | `POST /api/internal/orgs/{org_id}/deals` |
| `serx_get_deal_context` | RO | Returns a rich deal context payload including account, contact, proposal, and related meetings. This tool is designed for agent decision quality, not raw table dumping, so context comes pre-joined in a high-signal shape. It is the preferred read tool before any status transition. | `org_id`, `deal_id` | `GET /api/internal/orgs/{org_id}/deals/{deal_id}` |
| `serx_update_deal` | IDEMP | Updates deal state and metadata while enforcing transition constraints such as `lost_reason` for lost deals. This tool can auto-set closure timestamps and account lifecycle updates on win transitions. It returns refreshed rich deal context rather than a bare row for immediate downstream action. | `org_id`, `deal_id`, optional `title/status/value/source/notes/lost_reason` | `PUT /api/internal/orgs/{org_id}/deals/{deal_id}` |
| `serx_link_proposal_to_deal` | IDEMP | Links a proposal to a deal and advances deal status to `proposal_sent` in one operation. This tool guarantees proposal existence and org ownership before mutation to avoid cross-tenant errors. It returns full updated deal context for negotiation-stage automation. | `org_id`, `deal_id`, `proposal_id` | `PUT /api/internal/orgs/{org_id}/deals/{deal_id}/proposal` |

### 5.3 Internal Read/Admin Support (Accounts, Contacts, Proposals, Delivery, Work Objects)

| Tool | Kind | Description | Input schema summary | Wraps |
|---|---|---|---|---|
| `serx_list_orgs` | RO | Lists organizations available to internal automation. This tool is used for diagnostics, onboarding validation, and mapping audits. The response is intentionally compact with identity and domain fields only. | none | `GET /api/internal/orgs` |
| `serx_list_org_services_internal` | RO | Lists active services for a target organization from the internal API surface. This tool helps agents map proposal items and pricing options before creation actions. It supports bounded pagination with sensible limits to avoid context bloat. | `org_id`, optional `limit` | `GET /api/internal/orgs/{org_id}/services` |
| `serx_create_service_internal` | MUT | Creates a service for any organization through internal admin capability. This tool validates org existence and standardizes currency/public flags for consistent downstream usage. It returns the created service row to support immediate linking in proposal workflows. | `org_id`, `name`, optional `description`, `recurring`, `currency`, `price`, `public` | `POST /api/internal/services` |
| `serx_create_proposal_internal` | MUT | Creates and sends a proposal in one internal operation including proposal items and outbound email trigger. This tool validates service references and computes totals so agents do not manually orchestrate item-level inserts. It returns serialized proposal data including signing URL for immediate handoff. | org/contact/account fields, `items[]`, optional email subject/body | `POST /api/internal/proposals` |
| `serx_list_accounts` | RO | Lists accounts for an org with optional search support over name/domain. This tool is the primary account discovery mechanism prior to contact/deal operations. Results are ordered recent-first and bounded for model context efficiency. | `org_id`, optional `limit`, optional `search` | `GET /api/internal/orgs/{org_id}/accounts` |
| `serx_get_account` | RO | Fetches a single account by ID within org scope. This tool is used to confirm lifecycle/source/domain fields before deal progression. It returns a precise not-found error when account scope is invalid. | `org_id`, `account_id` | `GET /api/internal/orgs/{org_id}/accounts/{account_id}` |
| `serx_list_contacts` | RO | Lists contacts for an org with optional account filter and text search. This tool supports attendee-to-contact reconciliation and outreach preparation tasks. It returns joined account name metadata to avoid redundant follow-up calls. | `org_id`, optional `limit`, optional `account_id`, optional `search` | `GET /api/internal/orgs/{org_id}/contacts` |
| `serx_get_contact` | RO | Fetches a single contact with linked account metadata in org scope. This tool is useful for verifying deal primary contact and communication targets. It provides deterministic 404 semantics for invalid scope. | `org_id`, `contact_id` | `GET /api/internal/orgs/{org_id}/contacts/{contact_id}` |
| `serx_list_proposals_internal` | RO | Lists proposals for an org with optional status filter and includes serialized item data. This tool supports sales-stage checks and proposal aging analysis. Responses are normalized to human-readable status plus numeric status for automation logic. | `org_id`, optional `limit`, optional `status` | `GET /api/internal/orgs/{org_id}/proposals` |
| `serx_get_proposal_internal` | RO | Retrieves a single proposal with full item serialization. This tool is used for signability checks, total verification, and cross-linking into deals. It returns consistent signing URL formatting in the serialized payload. | `org_id`, `proposal_id` | `GET /api/internal/orgs/{org_id}/proposals/{proposal_id}` |
| `serx_get_proposal_deliverables` | RO | Retrieves deliverables for a signed proposal including engagement, projects, and order context. This tool enables post-sale orchestration and client-ready summaries without manual joins. It validates that the proposal is signed and fails with clear guidance otherwise. | `org_id`, `proposal_id` | `GET /api/internal/orgs/{org_id}/proposals/{proposal_id}/deliverables` |
| `serx_list_engagements` | RO | Lists engagements for an org with status/account filtering and project snippets. This tool supports operational workload awareness after deals are won. It returns high-signal relational context while remaining bounded by `limit`. | `org_id`, optional `limit`, `status`, `account_id` | `GET /api/internal/orgs/{org_id}/engagements` |
| `serx_get_engagement` | RO | Fetches a specific engagement and embedded projects/services context. This tool helps agents reason about delivery progression and blocked work. It is ideal for generating status briefs or handoff updates. | `org_id`, `engagement_id` | `GET /api/internal/orgs/{org_id}/engagements/{engagement_id}` |
| `serx_list_projects` | RO | Lists projects for an org with status/engagement filtering and service linkage. This tool provides execution visibility tied back to sold services. Output is constrained for context efficiency and sorted by recency. | `org_id`, optional `limit`, optional `status`, optional `engagement_id` | `GET /api/internal/orgs/{org_id}/projects` |
| `serx_get_project` | RO | Retrieves one project including service and engagement relationship fields. This tool is used for precise delivery diagnostics and proposal-to-project traceability. It returns not-found with org scope protection. | `org_id`, `project_id` | `GET /api/internal/orgs/{org_id}/projects/{project_id}` |
| `serx_list_orders_internal` | RO | Lists orders for an org with status/account filtering. This tool supports financial and delivery reconciliation alongside deal state. Responses include linked account metadata for concise reporting. | `org_id`, optional `limit`, optional `status`, optional `account_id` | `GET /api/internal/orgs/{org_id}/orders` |
| `serx_get_order_internal` | RO | Fetches one order with account and engagement linkage. This tool is a focused read primitive for payment/state troubleshooting in workflow automations. It uses strict org scoping and deterministic not-found handling. | `org_id`, `order_id` | `GET /api/internal/orgs/{org_id}/orders/{order_id}` |

### 5.4 Next.js OpenAPI-Specified Surface (Comprehensive Coverage Layer)

| Tool | Kind | Description | Input schema summary | Wraps |
|---|---|---|---|---|
| `serx_health_check` | RO | Returns service health from the API edge layer to verify route availability. This tool is useful as an initial connectivity probe before mutating workflows. It returns lightweight status information only. | none | `GET /api/health` |
| `serx_list_clients` | RO | Lists clients with pagination/filter support from the public API layer. This tool is the baseline discovery primitive for client-oriented workflows and batch operations. It returns paginated metadata so agents can iterate safely. | `limit`, `page`, `sort`, optional filters (`email`, `status`) | `GET /api/clients` |
| `serx_create_client` | MUT | Creates a new client record with required identity fields. This tool should be used when onboarding entities not already represented in contacts/accounts layers. It returns the canonical created client object. | required `email`, `name_f`, `name_l`; optional additional fields | `POST /api/clients` |
| `serx_get_client` | RO | Retrieves a specific client by identifier for targeted verification or enrichment. This tool avoids list scanning when ID is known and keeps output focused. It emits clear not-found messages for stale references. | `client_id` | `GET /api/clients/{client}` |
| `serx_update_client` | MUT | Updates mutable client fields for profile maintenance and correction workflows. This tool supports partial updates and returns the resulting canonical client state. It should be preferred over delete/recreate patterns to preserve history continuity. | `client_id`, patch payload | `PUT /api/clients/{client}` |
| `serx_delete_client` | DEST | Performs logical deletion semantics for a client record via API contract. This tool should only be used when data lifecycle policy requires removal from active workflows. It returns success/no-content semantics and should be guarded in agent prompts. | `client_id` | `DELETE /api/clients/{client}` |
| `serx_list_services` | RO | Lists available services from the external API layer for catalog discovery. This tool provides the inventory basis for proposal and order composition workflows. Results should be paged/filtered in follow-up calls where volume grows. | optional pagination/filter fields as available | `GET /api/services` |
| `serx_create_service` | MUT | Creates a service in the external API layer where client-facing catalog operations are needed. This tool is useful when internal admin flow is not appropriate. It returns the created service entity for immediate linkage. | service payload | `POST /api/services` |
| `serx_get_service` | RO | Retrieves a service by ID for validation and downstream pricing logic. This tool keeps reads precise and avoids full list context costs. It returns not-found explicitly if ID is invalid. | `service_id` | `GET /api/services/{id}` |
| `serx_update_service` | MUT | Updates service details such as pricing, description, and visibility controls. This tool supports incremental catalog maintenance without replacing service identities. It returns updated service state for audit trails. | `service_id`, patch payload | `PUT /api/services/{id}` |
| `serx_delete_service` | DEST | Deletes/deactivates a service from the external API contract. This tool should be constrained to explicit cleanup workflows because downstream objects may reference services. It returns no-content semantics on success. | `service_id` | `DELETE /api/services/{id}` |
| `serx_list_order_messages` | RO | Lists messages for an order thread to support conversation-aware automation. This tool helps agents summarize communication history before actions. Output is scoped to a single order for signal density. | `order_id` | `GET /api/orders/{id}/messages` |
| `serx_create_order_message` | MUT | Creates a new message in an order thread for workflow updates or handoff notes. This tool should be used to preserve chronological communication context. It returns the created message object for immediate confirmation. | `order_id`, message payload | `POST /api/orders/{id}/messages` |
| `serx_delete_order_message` | DEST | Deletes an order message when removal is policy-compliant or correction is mandatory. This tool is destructive and should be guarded by explicit agent instructions. It returns success/no-content behavior. | `order_message_id` | `DELETE /api/order-messages/{id}` |
| `serx_list_order_tasks` | RO | Lists tasks attached to a specific order for execution planning. This tool allows agents to inspect status and assign next steps without mutating state. It should be combined with task update tools for lifecycle progression. | `order_id` | `GET /api/orders/{id}/tasks` |
| `serx_create_order_task` | MUT | Creates a task under an order to track operational work. This tool is used when new actionable units emerge from meetings or proposal outcomes. It returns the created task for direct follow-up actions. | `order_id`, task payload | `POST /api/orders/{id}/tasks` |
| `serx_update_order_task` | MUT | Updates task content or status fields for order execution workflows. This tool enables iterative task management without replacing task identity. It returns the updated task entity for verification. | `task_id`, patch payload | `PUT /api/order-tasks/{id}` |
| `serx_delete_order_task` | DEST | Removes an order task when invalid or obsolete. This tool is destructive and should be used only with explicit intent and policy checks. It returns success/no-content semantics. | `task_id` | `DELETE /api/order-tasks/{id}` |
| `serx_list_proposals` | RO | Lists proposals to support sales pipeline visibility and stage analytics. This tool returns proposal summaries that can be filtered or expanded with retrieve calls. It is a key read primitive before send/sign operations. | list params | `GET /api/proposals` |
| `serx_get_proposal` | RO | Retrieves a proposal by ID for exact state checks and signing readiness validation. This tool is optimized for targeted reads in negotiation workflows. It emits deterministic not-found behavior for stale IDs. | `proposal_id` | `GET /api/proposals/{id}` |
| `serx_create_proposal` | MUT | Creates a proposal via external API path where public-facing proposal flows are used. This tool is useful when internal admin proposal tooling is not part of the orchestrated path. It returns created proposal details for immediate next steps. | proposal payload | `POST /api/proposals` |
| `serx_send_proposal` | MUT | Sends a proposal and advances communication state in one API operation. This tool is used when proposal content is finalized and client outreach should begin. It returns updated proposal status details. | `proposal_id`, optional send payload | `PATCH /api/proposals/{id}/send` |
| `serx_sign_proposal` | MUT | Signs a proposal and triggers downstream conversion behavior per API contract. This tool should be called only when signature criteria are met and authenticated context is valid. It returns conversion-linked state for subsequent execution tools. | `proposal_id`, signature payload | `PATCH /api/proposals/{id}/sign` |

### 5.5 Next.js route-only coverage (implemented in `app/api`, not in current `openapi/routes` set)

| Tool | Kind | Description | Input schema summary | Wraps |
|---|---|---|---|---|
| `serx_list_orders` | RO | Lists orders from the Next API implementation layer. This tool gives broad order visibility for downstream financial and delivery workflows. It should be paginated to control context size. | list params | `GET /api/orders` |
| `serx_create_order` | MUT | Creates an order and returns canonical order state for chained invoice/task operations. This tool should be used once service/client mappings are validated. It enforces required fields through API validation rules. | order payload | `POST /api/orders` |
| `serx_get_order` | RO | Retrieves a specific order by ID for targeted decision-making. This tool is preferred to list scanning when an order reference already exists. It returns deterministic not-found errors when stale. | `order_id` | `GET /api/orders/{id}` |
| `serx_update_order` | MUT | Updates mutable order fields for execution and billing transitions. This tool supports partial updates and returns updated order state. It should be used rather than delete/recreate to preserve history. | `order_id`, patch payload | `PUT /api/orders/{id}` |
| `serx_delete_order` | DEST | Deletes/deactivates an order according to API lifecycle rules. This tool is destructive and should be used with explicit policy alignment. It returns success/no-content contract behavior. | `order_id` | `DELETE /api/orders/{id}` |
| `serx_mark_order_task_complete` | MUT | Marks an order task complete via dedicated completion route. This tool exists for clarity when completion semantics differ from generic update behavior. It returns updated task completion state suitable for reporting. | `task_id`, optional completion payload | `POST /api/order-tasks/{id}/complete` |
| `serx_mark_order_task_incomplete` | MUT | Reverts completion status on an order task via dedicated route. This tool supports correction workflows when work is reopened. It returns updated task state for orchestration consistency. | `task_id` | `DELETE /api/order-tasks/{id}/complete` |
| `serx_list_invoices` | RO | Lists invoices for financial tracking and payment operations. This tool should be used before charge/mark-paid actions to confirm status and totals. It returns paginated invoice summaries where available. | list params | `GET /api/invoices` |
| `serx_create_invoice` | MUT | Creates an invoice and returns canonical billing object details. This tool is used after order scoping and pricing confirmation are complete. It should be chained with charge or mark-paid based on payment path. | invoice payload | `POST /api/invoices` |
| `serx_get_invoice` | RO | Retrieves a specific invoice by ID for precise billing state validation. This tool avoids unnecessary list reads and supports retry-safe payment orchestration. It returns clear not-found semantics. | `invoice_id` | `GET /api/invoices/{id}` |
| `serx_update_invoice` | MUT | Updates invoice fields while preserving invoice identity and historical linkage. This tool supports correction and reconciliation flows before payment completion. It returns updated invoice object state. | `invoice_id`, patch payload | `PUT /api/invoices/{id}` |
| `serx_delete_invoice` | DEST | Deletes/deactivates an invoice when policy permits. This tool is destructive and should be constrained with explicit prompts and operator safeguards. It returns success/no-content behavior. | `invoice_id` | `DELETE /api/invoices/{id}` |
| `serx_charge_invoice` | MUT | Attempts invoice charging through configured payment rails and records resulting payment state. This tool should be used when invoice data is final and payment method context is valid. It returns high-signal payment result fields for immediate branching decisions. | `invoice_id`, charge payload | `POST /api/invoices/{id}/charge` |
| `serx_mark_invoice_paid` | MUT | Marks invoice as paid for out-of-band settlement paths. This tool is useful for manual wire/check reconciliation where direct charge is not performed. It returns updated payment status metadata for reporting. | `invoice_id`, optional mark-paid payload | `POST /api/invoices/{id}/mark_paid` |
| `serx_list_tickets` | RO | Lists support tickets for customer operations workflows. This tool provides support context that can influence deal and account health decisions. It should be paginated to avoid large context windows. | list params | `GET /api/tickets` |
| `serx_create_ticket` | MUT | Creates a support ticket tied to customer context. This tool is useful when meetings or delivery signals reveal service issues requiring tracking. It returns created ticket data for assignment workflows. | ticket payload | `POST /api/tickets` |
| `serx_get_ticket` | RO | Retrieves a ticket by ID for precise incident/status inspection. This tool is preferred in follow-up workflows where ticket references already exist. It returns deterministic not-found responses when invalid. | `ticket_id` | `GET /api/tickets/{id}` |
| `serx_update_ticket` | MUT | Updates ticket fields such as status, notes, and assignment metadata. This tool supports ongoing support lifecycle management without recreating records. It returns updated ticket state for immediate downstream usage. | `ticket_id`, patch payload | `PUT /api/tickets/{id}` |
| `serx_delete_ticket` | DEST | Deletes/deactivates a ticket based on support policy and retention requirements. This tool is destructive and should only run with explicit intent. It returns success/no-content semantics. | `ticket_id` | `DELETE /api/tickets/{id}` |

---

## 6) Cal.com Lifecycle Workflow Tools: Atomic vs Compound

### Required atomic primitives (keep)

- `serx_resolve_org_from_event_type`
- `serx_create_cal_raw_event`
- `serx_create_booking_event`
- `serx_bulk_upsert_booking_attendees`
- `serx_create_meeting_from_cal_event`
- `serx_create_deal_from_meeting`
- `serx_update_meeting`
- `serx_update_deal`
- `serx_mark_cal_raw_event_processed`

### Proposed compound tools (small curated set)

1. `serx_process_new_booking`  
   Chain: resolve org -> create raw event -> create booking event -> upsert attendees -> create/dedupe meeting -> create deal if qualified -> mark raw processed.

2. `serx_process_booking_reschedule`  
   Chain: resolve org -> create raw event -> create booking event -> upsert attendees -> create/dedupe meeting with `rescheduled_from_uid` -> mark raw processed.

3. `serx_process_booking_cancelled`  
   Chain: resolve org -> create raw event -> create booking event -> find meeting -> set meeting cancelled -> update linked deal to lost/cancelled strategy -> mark raw processed.

4. `serx_process_meeting_ended`  
   Chain: resolve org -> create raw event -> create booking event -> find meeting -> update meeting completion/no-show flags -> advance deal stage/status -> mark raw processed.

### Recommendation

- **Primary guidance:** keep orchestration mostly agent-composed using atomic tools (best-practice default).
- **Add the four compound tools above as guardrailed convenience tools** for high-volume webhook intake where strict ordering and retries matter.
- Compound tools must internally call the same atomic services, return step-by-step sub-results, and expose partial-failure diagnostics so they do not become opaque business-logic black boxes.

---

## 7) Schema Generation Strategy (OpenAPI -> MCP Zod)

### Recommendation: Hybrid auto-generation

1. **Auto-generate 80-90%** from `openapi/routes/**` metadata.
2. **Manual overlays** for:
   - compound workflow tools
   - richer descriptions (3-4 sentence minimum)
   - enum constraints and pagination consistency
   - output trimming/high-signal shaping

### Transformer design

- Input: `RouteMetadata` objects (method/path/params/requestBody/responses).
- Transform:
  - `operationId` -> `serx_<snake_case_operation>`
  - query/path/body schema -> Zod `inputSchema`
  - method semantics -> annotation defaults:
    - `GET` => `readOnlyHint=true`, `idempotentHint=true`, `destructiveHint=false`
    - `POST` => `readOnlyHint=false`, `idempotentHint=false` (override per endpoint)
    - `PUT/PATCH` => `idempotentHint=true` by default unless known side effects
    - `DELETE` => `destructiveHint=true`
  - produce tool registration stubs with endpoint wrapper call metadata
  - generate `outputSchema` candidates from OpenAPI success responses; overlays tighten shape to high-signal fields
- Output artifact:
  - generated `tool-spec.generated.ts` plus checked-in manual `tool-spec.overrides.ts`
  - generated drift report comparing OpenAPI operations vs registered tools

### Why hybrid

- Full manual does not scale and drifts quickly.
- Full auto lacks domain-aware descriptions and response shaping quality.
- Hybrid preserves coverage and maintainability while meeting MCP usability standards.

---

## 8) Resource + Prompt Design (Forward-Compatible)

Even though current Anthropic connector is tool-only, design full MCP spec support now.

### Candidate MCP resources

- `serx://org/{org_id}/deal/{deal_id}/context` (deal + linked account/contact/proposal/meetings snapshot)
- `serx://org/{org_id}/meeting/{meeting_id}/timeline`
- `serx://cal/booking/{uid}/events`
- `serx://org/{org_id}/account/{account_id}/summary`
- `serx://org/{org_id}/proposal/{proposal_id}/deliverables`

### Candidate prompt templates

- `serx_prompt_sales_briefing_from_deal_context`
- `serx_prompt_post_meeting_followup_email`
- `serx_prompt_proposal_revision_recommendations`
- `serx_prompt_pipeline_risk_assessment`
- `serx_prompt_booking_exception_triage`

Design these as optional registration modules gated behind feature flags until connector support lands.

---

## 9) Phased Implementation Roadmap

## Phase 1: MVP (Cal intake end-to-end)

Deliverables:
- MCP server skeleton (`registerTool`, streamable HTTP, auth middleware)
- Atomic tools for full Cal booking/deal lifecycle
- 2 compound tools minimum: `serx_process_new_booking`, `serx_process_booking_cancelled`
- Structured error taxonomy + actionable hints
- Railway deployment + Doppler wiring + health checks
- Baseline observability: request ids, per-tool latency, upstream status code, redacted logs

Success criteria:
- Managed Agent can process BOOKING_CREATED, BOOKING_RESCHEDULED, BOOKING_CANCELLED, MEETING_ENDED without manual intervention.
- Retry-safe behavior validated with duplicate event replay.

## Phase 2: Complete internal business context coverage

Deliverables:
- Internal read/admin tools (`accounts`, `contacts`, `proposals`, `engagements`, `projects`, `orders`)
- Rich context shaping and response truncation/pagination policy
- Tool-level observability (latency, error code, token-safe logs)
- Idempotency audit + annotation correction pass across all mutation tools

## Phase 3: Next.js API comprehensive coverage

Deliverables:
- Auto-generated + overridden tool registrations from `openapi/routes/**`
- Route-only gap tools from `app/api/**` not represented in current OpenAPI metadata
- Consistent tool naming, annotations, and idempotency declarations

## Phase 4: Resources + prompts + eval suite

Deliverables:
- Register resources/prompt templates behind feature flags
- Create 10 evaluation questions and verified answers
- Run evaluation harness and capture baseline scorecard
- Emit eval XML artifact at `eval/evaluation.xml` with exact-string answers

## Phase 5: Hardening + governance

Deliverables:
- Rate limits per tool family
- Allowlist/denylist for destructive tools
- Audit log + incident playbooks
- Drift checks between API metadata and tool catalog

---

## 10) Evaluation Plan (10 Questions)

Per mcp-builder Phase 4, define stable, read-only, multi-hop questions:

1. For a fixed historical week, which organizer domain produced the highest count of `BOOKING_CREATED` events for business-email attendees?
2. For a known booking UID with reschedule history, what is the final scheduled start time in ISO UTC?
3. For a specific org and month, how many meetings ended with `guest_no_show=true` and had an associated deal?
4. Among deals created from Cal in a fixed window, which source value appears most frequently?
5. For a fixed proposal ID, what is the exact signed deliverables project count?
6. For a known account, what is the most recent meeting status and linked deal status pair?
7. For a fixed booking UID, did attendee role counts include at least one host? (answer `true`/`false`)
8. Which lost deal in a fixed sample has the highest declared value and what is its `lost_reason`?
9. For a fixed org, which project phase label appears most across active projects?
10. For one fixed invoice sample set, how many are marked paid versus charged-but-unpaid?

Evaluation requirements:
- All answers verifiable by exact string comparison.
- No destructive tools used during eval.
- Use small page sizes (`limit <= 10`) and multi-call reasoning.
- Questions must be fully independent and anchored to fixed historical entities/intervals to avoid answer drift.
- Final output format must follow:
  - `<evaluation><qa_pair><question>...</question><answer>...</answer></qa_pair>...</evaluation>`

---

## 10.1 Implementation quality gates

Before production cutover:
- `npm run build` passes with strict TypeScript checks.
- MCP Inspector validation run against deployed/staging endpoint succeeds for representative tool families.
- Smoke tests confirm auth failures are actionable and non-leaky.
- Destructive tools are disabled by default and require explicit runtime allowlist.

---

## 11) Error Message Contract (Applies to Every Tool)

Every tool returns:
- concise error category (`auth_error`, `validation_error`, `not_found`, `conflict`, `upstream_error`)
- actionable message with next step
- optional `retryable` boolean
- optional `suggested_tools` array

Example:
- `"Deal not found in org scope. Verify org_id/deal_id pair with serx_get_deal_context before update."`

---

## 12) Final Recommendation Summary

- Build **dedicated Railway MCP service** in TypeScript using **Streamable HTTP**.
- Use **hybrid generation** for broad API coverage with manual quality overlays.
- Keep **atomic tools as primary**, add a **small set of compound lifecycle tools** for resilient webhook orchestration.
- Standardize auth with **Managed Agent bearer ingress** + **server-side internal key egress**.
- Ship in phases, with Phase 1 focused strictly on **Cal intake -> meeting/deal lifecycle completion**.
