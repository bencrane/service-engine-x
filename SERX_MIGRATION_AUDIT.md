# SERX Migration Audit

Scope: state-of-the-codebase audit of `service-engine-x` (SERX) to inform porting its live functionality into `outbound-engine-x` (OEX). Research-only; no SERX code modified.

Working tree: `/Users/benjamincrane/service-engine-x/.claude/worktrees/silly-colden-0b396f`

---

## 1. Functional inventory

What SERX is, today, by capability area:

### 1.1 Cal.com webhook ingest and normalization (LIVE)
- HMAC-verified webhook receiver: `service-engine-x-api/app/routers/cal_webhooks.py:1` — POST `/api/webhooks/cal` validates `X-Cal-Signature-256` against `CAL_WEBHOOK_SECRET`, persists to `cal_raw_events`, then dispatches to `route_cal_event`.
- Parallel raw-sink (no HMAC) for forensic capture: `service-engine-x-api/app/routers/calcom_webhooks.py:1` — POST `/api/webhooks/calcom` writes immutable rows to `cal_webhook_events_raw`.
- Normalization tables populated: `cal_booking_events`, `cal_booking_attendees`, `cal_recordings` (migration `014_replace_calcom_webhook_log_with_cal_normalization_tables.sql`).
- In-process event handlers are stubs: `service-engine-x-api/app/services/cal_event_handlers.py` — `BOOKING_CREATED`, `BOOKING_RESCHEDULED`, `BOOKING_CANCELLED`, `MEETING_ENDED` all currently mark processed without business logic.

### 1.2 Proposals (LIVE — "Chica Chida")
- Authenticated CRUD + signing at `/api/proposals/*`: `service-engine-x-api/app/routers/proposals.py` (router).
- Public, unauthenticated viewer + payment kickoff at `/api/public/proposals/*`: same file (`public_router`, line ~1413+). Endpoints include `get_public_proposal`, `public_create_checkout`, `public_create_payment_intent`, `get_signed_pdf`, `public_sign_proposal`.
- PDF generation via DocRaptor (`DOCRAPTOR_API_KEY`).
- Email send via Resend: `service-engine-x-api/app/services/resend_service.py` (templates include hardcoded Modern Full bank info: Choice Financial, routing `091311229`, acct `202314840766`, in `send_proposal_signed_email`).
- Public proposal URL is hardcoded: `https://revenueactivation.com/p/{proposal_id}` (`proposals.py:934`).
- Signing flow writes to `proposal_signatures` (migration `010_add_proposal_signatures.sql`).

### 1.3 Stripe payments (PARTIAL — checkout flows wired, fulfillment stubs)
- Service: `service-engine-x-api/app/services/stripe_service.py` — checkout session creation, line items builder, webhook signature verification.
- Webhook handler at `/api/webhooks/stripe` lives inside `proposals.py` (`webhook_router`).
- `stripe_*` columns on proposals/orgs: migrations `004_add_stripe_fields.sql`, `009_add_stripe_publishable_key.sql`.

### 1.4 Internal dispatcher / scheduler (LIVE, cross-service)
- POST `/api/internal/scheduler/dispatch-due-preframes` in `service-engine-x-api/app/routers/internal_scheduler.py` — queries due meetings, inserts to `webhook_events_raw`, dispatches to OPEX `/events/receive` using `OPEX_API_URL` + `OPEX_AUTH_TOKEN`.
- Pre-frame window driven by columns added in `019_scheduler_preframe.sql`.

### 1.5 CRM/engagement model (LIVE CRUD, usage thin)
- Routers: `accounts.py`, `contacts.py`, `clients.py`, `engagements.py`, `projects.py`, `conversations.py`, `orders.py`, `order_tasks.py`, `order_messages.py`, `services.py`, `invoices.py`, `tickets.py` — standard CRUD, gated by `get_current_org`.
- `meetings.py`, `bank_details.py`, `orgs.py`, `users.py` — list-style endpoints.

### 1.6 Internal admin surface (LIVE — service-token gated)
- `service-engine-x-api/app/routers/internal.py` — admin endpoints across orgs, services, proposals, accounts/contacts, engagements, projects, orders. Hardcoded `SIGNING_URL_BASE`.
- `service-engine-x-api/app/routers/internal_cal_events.py` — 14 endpoints reading `cal_raw_events`, `cal_booking_events`, `cal_booking_attendees`, `cal_recordings`.
- `service-engine-x-api/app/routers/internal_meetings_deals.py` — `resolve-org`, `resolve-org-from-team`, meetings, deals, link-proposal endpoints.
- `service-engine-x-api/app/routers/internal_webhook_events.py` — single-row reader on `webhook_events_raw`.

### 1.7 Customer portal (SCAFFOLDING)
- `lib/auth.ts` (Next.js, legacy) implements bcrypt, sessions, `api_tokens` — superseded but not deleted. No production portal traffic; the FastAPI public proposal viewer is the only customer-facing surface.

### 1.8 Multi-tenant org infra (SCAFFOLDING)
- Org model, sentinel UUIDs (Revenue Activation `11111111-...`, Outbound Solutions `2222...`, Modern Full) baked into seeds and code. Auth has been collapsed to a single shared bearer token, so multi-tenant gating relies on caller-supplied `org_id` query params rather than enforcement (see Section 7).

---

## 2. Database schema

Source: `migrations/001-004` at repo root + `service-engine-x-api/migrations/002-021`. Unique tables, derived from migrations cross-referenced with `client.table("…")` usage in `app/`:

Core identity / tenancy:
- `orgs`, `users`, `org_members`
- `api_tokens` (legacy Next.js auth — `lib/auth.ts`)
- `org_bank_details` (`011_add_org_bank_details.sql`)

CRM:
- `accounts`, `contacts` (`006_add_accounts_contacts.sql`, `007_migrate_clients_to_accounts.sql`)
- `clients` (legacy — superseded by accounts)
- `engagements`, `projects` (`002_add_engagement_model.sql`)
- `conversations` (`003_conversations_project_scoped.sql`)
- `services`, `service_offerings`
- `orders`, `order_tasks`, `order_messages`
- `invoices`, `tickets`

Proposals + signing:
- `proposals` (root `002_add_proposals_system.sql`; project-centric items in `003_proposal_items_project_centric.sql`)
- `proposal_items`
- `proposal_signatures` (`010_add_proposal_signatures.sql`)
- Stripe columns added by `004_add_stripe_fields.sql` and `009_add_stripe_publishable_key.sql`
- Documenso columns added by root `004_add_documenso_to_proposals.sql`

Cal.com / meetings:
- `cal_raw_events` (`016_cal_raw_events.sql`) — in-process routing input
- `cal_webhook_events_raw` — immutable audit sink (replaced earlier `calcom_webhook_log` per `014_…`)
- `cal_booking_events`, `cal_booking_attendees`, `cal_recordings` (`014_…`, constraint fix in `015_fix_cal_booking_attendees_upsert_constraint.sql`)
- `cal_event_type_cache` (`013_add_meetings_deals_and_cal_event_type_cache.sql`)
- `cal_webhook_agent_routes` + task template (`017_…`, `018_…`) — wired for an external Pipedream worker; not consumed by in-process handlers
- `meetings`, `deals` (`013_…`, custom fields in `019_add_meetings_custom_fields.sql`, cancellation reason in `020_add_meetings_cancellation_reason.sql`)

Scheduler / events:
- `webhook_events_raw` — used by `internal_scheduler.py` to publish synthetic events to OPEX
- Scheduler preframe columns on `meetings` (`019_scheduler_preframe.sql`)

Misc / dropped:
- `notification_email` column (`005_add_notification_email.sql`)
- `systems` table — added in `005b_add_systems.sql`, dropped in `008_drop_systems.sql`
- Source-slug rename: `021_rename_cal_com_source_to_cal_com.sql` (rewrites `accounts.source`/`deals.source` from `cal.com` → `cal_com`).

---

## 3. API surface inventory

`service-engine-x-api/app/main.py` mounts 26 routers. Inventory grouped by auth posture:

### 3.1 Public, unauthenticated
- `/api/public/proposals/{id}` — viewer (`proposals.py` public_router)
- `/api/public/proposals/{id}/checkout` — Stripe Checkout session
- `/api/public/proposals/{id}/payment-intent` — Stripe PaymentIntent
- `/api/public/proposals/{id}/sign` — accept signature
- `/api/public/proposals/{id}/signed-pdf` — signed PDF retrieval

### 3.2 Webhook receivers (signed by upstream — no SERX bearer)
- POST `/api/webhooks/cal` (HMAC-SHA256 via `CAL_WEBHOOK_SECRET`)
- POST `/api/webhooks/calcom` (raw sink, no signature)
- POST `/api/webhooks/stripe` (Stripe signature verified in `stripe_service.py`)

### 3.3 Authenticated CRUD (bearer + `org_id`/`user_id` query)
- `/api/orgs`, `/api/users`, `/api/accounts`, `/api/contacts`, `/api/clients`
- `/api/engagements`, `/api/projects`, `/api/conversations`
- `/api/services`, `/api/orders`, `/api/order-tasks`, `/api/order-messages`
- `/api/invoices`, `/api/tickets`
- `/api/meetings`, `/api/bank-details`
- `/api/proposals/*` (authenticated counterpart of public viewer)

### 3.4 Internal (service-token gated, `verify_token` only — no org_id)
- `/api/internal/*` — `internal.py` admin (orgs/services/proposals/accounts/contacts/engagements/projects/orders).
- `/api/internal/cal-events/*` — 14 endpoints in `internal_cal_events.py`.
- `/api/internal/meetings-deals/*` — resolve-org, meetings, deals, link-proposal (`internal_meetings_deals.py`).
- `/api/internal/scheduler/dispatch-due-preframes` — outbound dispatcher (`internal_scheduler.py`).
- `/api/internal/webhook-events/{id}` — single-row reader (`internal_webhook_events.py`).

Router export source: `service-engine-x-api/app/routers/__init__.py`.

---

## 4. External dependencies and integrations

| System | Purpose | Where |
|---|---|---|
| Supabase | DB + service-role client | `service-engine-x-api/app/database.py` |
| Cal.com (v2 API) | event types, fetches | `service-engine-x-api/app/services/calcom_client.py` |
| Cal.com webhooks | meeting lifecycle | `routers/cal_webhooks.py`, `routers/calcom_webhooks.py` |
| Stripe | checkout / payment intents / webhooks | `services/stripe_service.py` |
| Resend | transactional email | `services/resend_service.py` |
| DocRaptor | PDF rendering for proposals | invoked from `proposals.py` |
| OPEX (outbound-package-engine-x) | downstream event sink | `routers/internal_scheduler.py` (`OPEX_API_URL`, `OPEX_AUTH_TOKEN`) |
| Doppler | secret source (sole) | `doppler.yaml`, pinned to `service-engine-x-api/prd` |

Settings model: `service-engine-x-api/app/config.py` — `SERX_AUTH_TOKEN`, `SERX_API_BASE_URL`, `OPEX_API_URL`, `OPEX_AUTH_TOKEN`, `RESEND_API_KEY`, `DOCRAPTOR_API_KEY`, `CAL_API_KEY`, `CAL_WEBHOOK_SECRET`, scheduler windows, Stripe keys.

---

## 5. Inbound callers of SERX

Confirmed by grepping sibling repos for `SERX_`, `serviceengine.xyz`, and SERX route paths:

1. **`service-engine-x-mcp`** — primary. ~70 tools wrap SERX internal + service routes.
   - Env: `SERX_MCP_AUTH_TOKEN` (inbound bearer for MCP itself), `SERX_INTERNAL_API_BASE_URL`, `SERX_INTERNAL_API_KEY`, `SERX_SERVICE_API_TOKEN` (`service-engine-x-mcp/src/env.ts`).
   - Outbound auth: `service-engine-x-mcp/src/http-client.ts:43` — `internal` mode sends `x-internal-key`; `service` mode sends `Authorization: Bearer`.
   - Tool catalog: `service-engine-x-mcp/src/tool-catalog.ts`.
2. **`cal-mcp`** (sibling) — does not call SERX; wraps `@calcom/cal-mcp` via `auth-proxy.mjs`. Listed for completeness.
3. **In-repo Next.js dashboard** (legacy) — talks to Supabase directly via `lib/auth.ts`; not a SERX HTTP caller.
4. **Cal.com** — POSTs to `/api/webhooks/cal` and `/api/webhooks/calcom`.
5. **Stripe** — POSTs to `/api/webhooks/stripe`.
6. **Anonymous public proposal viewers** — browser traffic to `/api/public/proposals/*` and the hardcoded `revenueactivation.com/p/{id}` host.
7. **Trigger.dev / Railway cron / OPEX** — invokes `/api/internal/scheduler/dispatch-due-preframes` (Trigger.dev workflow has been collapsed; ongoing cron source needs operator confirmation).

Negative findings (no SERX coupling):
- `outbound-engine-x-frontend` — no `SERX_*` env, no `serviceengine.xyz` references.
- `comms-package`, `chat-package`, `billing-engine-x-api` — none reference SERX env or routes.

---

## 6. Outbound auth from SERX

- **To OPEX**: `routers/internal_scheduler.py` sends `Authorization: Bearer ${OPEX_AUTH_TOKEN}` to `${OPEX_API_URL}/events/receive`.
- **To Cal.com**: `services/calcom_client.py` sends `cal-api-version` and bearer token from `CAL_API_KEY`.
- **To Stripe**: SDK uses `STRIPE_SECRET_KEY`.
- **To Resend**: SDK uses `RESEND_API_KEY`.
- **To DocRaptor**: API key in request payload.
- **To Supabase**: service-role key via Supabase Python client.

---

## 7. The stripped-down auth state, documented

This is the intentional posture, not a bug.

- Single shared bearer token: `SERX_AUTH_TOKEN`. All authenticated routes accept it; no per-user JWT, no per-org key.
- Validation: `service-engine-x-api/app/auth/dependencies.py:19` `_check_token`.
- `verify_token` (token only): `auth/dependencies.py:58` — used for `/api/internal/*`.
- `get_current_org` (token + Query `org_id` + Query `user_id`): `auth/dependencies.py:65` — used for tenant CRUD.
- Org and user identity are **caller-supplied query parameters**. There is no enforcement that the caller is entitled to that org_id; the bearer holder is fully trusted.
- Public proposal routes (`/api/public/proposals/*`) require no token at all — they are intentionally anonymous so paying customers can view, sign, and pay without accounts.
- Legacy multi-tenant scaffolding (`api_tokens`, `org_members`, bcrypt sessions in `lib/auth.ts`) exists in DB and Next.js code but is not in the request path for the FastAPI service.

This collapse is a deliberate simplification while the live surface is small (proposals + Cal ingest + scheduler), and the only authenticated callers are SERX-controlled (`service-engine-x-mcp`, internal cron).

---

## 8. What's live vs scaffolding

Confirming or correcting operator's prior assessment:

| Area | Operator | Audit verdict |
|---|---|---|
| Cal webhook ingest | LIVE | **LIVE** — HMAC-verified, raw + normalized rows persisted. Event handlers downstream are stubs (Section 1.1). |
| Proposals ("Chica Chida") | LIVE | **LIVE** — full path: create, render PDF (DocRaptor), send (Resend), public view, sign, signed-PDF retrieval. |
| Payments | not started | **PARTIAL, not "not started"** — Stripe Checkout + PaymentIntent endpoints exist and can produce live sessions; webhook handler exists. Order/invoice fulfillment after payment is the unfinished piece. Reclassify as "wired but not closed-loop." |
| Customer portal | not started | **CONFIRMED not started** — only the anonymous proposal viewer; no logged-in portal. `lib/auth.ts` is dead infrastructure. |
| Multi-tenant org infra | scaffolding | **CONFIRMED scaffolding** — DB + sentinel UUIDs present; runtime auth flattened to single bearer; org_id is caller-supplied. |
| Internal scheduler → OPEX | (not in operator list) | **LIVE** — emits to OPEX `/events/receive`. Cadence/cron source is operationally external (Railway/Trigger.dev). |
| Cal in-process routing logic | (not in operator list) | **STUB** — `cal_event_handlers.py` returns processed without action. `cal_webhook_agent_routes` table is dormant in-process. |
| CRM CRUD (accounts/contacts/projects/orders/etc.) | (implicit) | **LIVE endpoints, low traffic** — endpoints work; production usage outside MCP appears minimal. |

---

## 9. Migration assessment

What to port into OEX, by area:

### 9.1 Port wholesale (clean lift)
- **Proposals end-to-end** — router, services, templates, signing flow, public viewer, hardcoded bank details extracted to config. This is the single biggest revenue-relevant artifact.
- **DocRaptor + Resend integration glue** — small, generic, useful in OEX.
- **Stripe checkout/payment-intent endpoints** — keep; wire to OEX's order/invoice tables.
- **Cal.com webhook receiver + HMAC verification + normalization tables** — port the receiver verbatim; reconsider whether OEX needs a separate raw-sink table or unifies on one.

### 9.2 Re-architect during port
- **Auth** — Don't bring `SERX_AUTH_TOKEN` collapse into OEX as-is. OEX should adopt its own posture (per-caller service tokens at minimum); the SERX collapse is an artifact of small surface area.
- **Internal scheduler dispatch** — In OEX, the dispatcher and the receiver may collapse into one process. The current `SERX → OPEX /events/receive` hop becomes unnecessary if OEX subsumes both ends.
- **Cal event handlers** — stubs in SERX. Define real OEX-side handlers during port (deal creation, meeting linkage, agent routing).
- **Hardcoded URLs and bank details** — `https://revenueactivation.com/p/{id}` and Modern Full bank info in `resend_service.py` must be parameterized per org/Doppler config.

### 9.3 Drop
- `lib/auth.ts` legacy bcrypt/session/api_tokens path.
- `clients` table (already superseded by accounts/contacts in SERX).
- `systems` table (already dropped).
- `cal_webhook_agent_routes` if the external Pipedream worker is decommissioned (operator decision — see Section 12).

### 9.4 Keep but defer
- Engagements/projects/orders/order_tasks/order_messages/invoices/tickets routers — port DDL, port routes, but real product use can wait until OEX customers need them.

---

## 10. Database migration considerations

- Migrations are split across two roots: repo root `migrations/001-004` (foundation: multi-tenant + proposals + documenso) and `service-engine-x-api/migrations/002-021` (engagement model, accounts, stripe, signatures, bank details, meetings/deals, cal normalization, scheduler preframe). When porting, flatten into a single OEX migration sequence.
- Sentinel UUIDs (`11111111-...` for Revenue Activation, `2222...` for Outbound Solutions, plus Modern Full) are seeded; decide whether OEX preserves them or generates fresh.
- Source-slug rename (`021_rename_cal_com_source_to_cal_com.sql`) sets a precedent: provider slugs use underscores. Honor in OEX schema.
- Cal raw-event split: `cal_raw_events` (in-process input) vs `cal_webhook_events_raw` (immutable audit). Decide if OEX keeps both or unifies.
- `webhook_events_raw` is the SERX→OPEX dispatch table; if OEX subsumes both ends, this table's role changes (becomes either internal queue or removable).
- `proposals.pdf_url` column existence not directly verified in the migrations I read end-to-end — confirm before porting (uncertain spot).

---

## 11. Webhook ingest considerations

- **Cal.com** — Two endpoints today:
  - `/api/webhooks/cal` (HMAC verified, dispatches in-process)
  - `/api/webhooks/calcom` (no signature, immutable audit)
  Decision needed: single ingest endpoint with both signature-verify and audit-write, or keep two for forensic redundancy.
- **Stripe** — webhook handler currently lives inside `proposals.py`. In OEX it should be its own router for clarity and to support payment events outside the proposal lifecycle.
- **Pipedream / external workers** — `cal_webhook_agent_routes` was designed to drive an external routing worker. If we keep external routing, the ingest layer must continue persisting `cal_raw_events` in the original shape; if we move routing in-process, that table can be simplified.
- **OPEX dispatch** — current `webhook_events_raw` insert + HTTP POST to OPEX is fire-and-forget with no retry table. Migration target should consider durable outbox.

---

## 12. Decisions that need to be made

1. **Auth model for OEX.** Single bearer (current SERX) vs scoped service tokens vs per-org keys. Recommend not inheriting the SERX collapse.
2. **Customer portal.** Build, defer, or stay anonymous-only via signed proposal URLs.
3. **`cal_webhook_agent_routes` and Pipedream worker.** Keep external, fold into OEX, or remove.
4. **Hardcoded `revenueactivation.com/p/` and Modern Full bank details.** Parameterize per-org or per-Doppler-config — must be resolved before porting `resend_service.py`.
5. **Stripe fulfillment closure.** Currently checkout creates a session; nothing closes the loop into orders/invoices on `payment_intent.succeeded`. Must specify in OEX.
6. **Scheduler ownership.** Whether OEX subsumes both the dispatcher (current SERX) and the receiver (current OPEX), eliminating the cross-service HTTP hop.
7. **Sentinel-org seeding.** Whether to carry `11111111-...` / `2222...` org UUIDs forward.
8. **Proposal hosting host/path.** New OEX customer-facing host — single domain or per-org subdomain.
9. **`api.serviceengine.xyz` cutover plan.** Currently rewritten by `proxy.ts`; production base URL not directly verified from code (uncertain spot).
10. **Doppler project layout.** Each engine-x project reads from its same-named Doppler project (per user memory). Confirm OEX gets its own project and never re-reads `service-engine-x-api`.

---

## 13. Risks and complications

- **Unauthenticated public routes** are a feature, not a bug — but the IDs in `/api/public/proposals/{id}` are UUIDs and the only access control is non-enumerability. Any port must preserve UUIDv4 issuance and consider rate-limiting.
- **Hardcoded bank details in `resend_service.py`** are a per-org leak risk if multi-org goes live before this is parameterized.
- **Stripe webhook handler co-located in `proposals.py`** — porting proposals without porting webhook signature verification breaks payments silently.
- **DocRaptor outage = no signed PDFs** — no fallback path. Consider whether OEX needs a queue/retry.
- **Cal handlers are stubs** — porting the ingest without porting (and writing) handlers means OEX captures events but doesn't act on them. Plan handler implementation as part of the cutover.
- **Cross-service dispatch (`SERX → OPEX`)** — token compromise or `OPEX_API_URL` misconfiguration silently fails. No retry/outbox in current code.
- **`cal_raw_events` vs `cal_webhook_events_raw` divergence** — two tables, two conventions; risk of drift if migration only ports one.
- **Sentinel UUIDs leaking into application logic** — search for hardcoded `11111111-...` and `2222...` before porting; these are scattered through seeds and a few code paths.
- **Production hostname / proxy setup** — `proxy.ts` rewrites `api.serviceengine.xyz` → `/api`. The actual production base URL chain (Railway → Doppler → DNS) was not verified end-to-end in this audit (uncertain spot).
- **Legacy `lib/auth.ts`** still present — if not removed during port, future maintainers may resurrect bcrypt/sessions path under the assumption it's the canonical auth.
- **Doppler context bleed** — historical issue (per `serx-mcp-deployment-state.md`): a shared Railway app caused env collisions. OEX should isolate its Railway app from day one.
