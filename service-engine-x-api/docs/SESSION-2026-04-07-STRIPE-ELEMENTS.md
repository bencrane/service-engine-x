# Work Session: 2026-04-07 — Stripe Elements & Proposal API Audit

## What Happened

Audited the entire proposal system in service-engine-x-api, discovered significant dead code, then built new Stripe payment endpoints for a frontend rebuild.

---

## Key Discoveries

### Documenso is Dead Code
The only code path that calls Documenso is `POST /api/proposals/{id}/send`, which requires `status=0` (Draft). But `POST /api/proposals` (Create) immediately sets `status=1` (Sent). The Send endpoint is unreachable. All Documenso config vars, the `upload_to_documenso()` function (lines 571-714), and the DB columns `documenso_document_id` / `documenso_signing_token` are dead. They haven't been removed from the codebase yet.

### No Draft State in Practice
Create = Send. There is no save-as-draft flow. The proposal is created with `status=1` and the email goes out immediately.

### DocRaptor IS Still Used
Used in the public sign flow (`POST /api/public/proposals/{id}/sign`) to generate a signed PDF server-side. The server has its own HTML template (`generate_signed_proposal_html()`), embeds the base64 signature as an `<img>`, sends to DocRaptor, uploads result to Supabase Storage.

### Stripe Keys Are Per-Org
Stored in the `organizations` table, not env vars. This is by design — multi-tenant, each org has its own Stripe account. Fields: `stripe_secret_key`, `stripe_publishable_key` (new), `stripe_webhook_secret`.

### Restricted Keys Work as Drop-In
`rk_live_...` keys work identically to `sk_live_...` in the Stripe SDK. No separate column needed. Stored in `stripe_secret_key`.

---

## What We Built

### Migration 009: `stripe_publishable_key`
- File: `service-engine-x-api/migrations/009_add_stripe_publishable_key.sql`
- Adds `stripe_publishable_key VARCHAR(255)` to `organizations` table
- Already run in production

### New Endpoint: `POST /api/public/proposals/{id}/payment-intent`
- No auth, no request body
- Looks up proposal items, sums prices, creates a Stripe PaymentIntent using the org's `stripe_secret_key`
- Returns `{ client_secret, payment_intent_id, amount }` (amount in cents)
- Frontend uses `client_secret` with `stripe.confirmPayment()` via Stripe Elements

### New Endpoint: `POST /api/public/proposals/{id}/checkout`
- No auth, no request body
- Creates a Stripe Checkout session from proposal items
- Returns `{ checkout_url, session_id }`
- Alternative to Elements — redirects user to Stripe-hosted page

### Updated: `GET /api/public/proposals/{id}`
- Now returns `org_slug`, `org_domain`, `stripe_publishable_key` in addition to existing fields
- Supabase join updated to fetch these from the organizations table

### Updated: `POST /api/webhooks/stripe`
- Now handles `payment_intent.succeeded` in addition to `checkout.session.completed`
- Refactored into `_handle_checkout_completed()` and `_handle_payment_intent_succeeded()` helper functions
- `payment_intent.succeeded` was added to the Stripe webhook destination in the dashboard (Rare Structure / Outbound Solutions account)

---

## Org Setup Done

**Outbound Solutions** (DBA of Rare Structure) in the `organizations` table now has:
- `stripe_secret_key` = restricted key (`rk_live_...`)
- `stripe_publishable_key` = `pk_live_51Sz...`
- `stripe_webhook_secret` = `whsec_...`
- `domain` = `outboundsolutions.com`

Webhook URL registered in Stripe: `https://api.serviceengine.xyz/api/webhooks/stripe`
Events: `checkout.session.completed`, `checkout.session.async_payment_failed`, `checkout.session.async_payment_succeeded`, `payment_intent.succeeded`

---

## Frontend Integration Pattern (Stripe Elements)

```
1. GET /api/public/proposals/{proposal_id}
   → { stripe_publishable_key, total, items, org_name, ... }

2. Initialize Stripe.js:
   const stripe = Stripe(stripe_publishable_key)
   Mount Payment Element

3. POST /api/public/proposals/{proposal_id}/payment-intent
   → { client_secret, amount }

4. stripe.confirmPayment({ clientSecret, elements, confirmParams: { return_url } })

5. Stripe webhook fires payment_intent.succeeded → backend processes
```

The frontend does NOT need to send amount, tenant ID, or any body — backend derives everything from the proposal ID.

---

## Context: Why This Was Built

Ben is rebuilding the frontend proposal experience in a separate app. For this immediate use case (Rare Structure / Outbound Solutions, $27,500 proposal):

- The proposal record will be inserted directly into Supabase (not via the API, to avoid the automatic email send)
- The frontend renders the proposal with hardcoded design, fetches price/org data from the public GET endpoint
- Payment via Stripe Elements (preferred) or ACH bank transfer (manual, no integration)
- No engagement/project/order creation needed for this one-off
- No e-signature capture needed for this one-off
- The signing link URL will be `outboundsolutions.com/p/{proposal_id}`

The plan is to evolve this into a non-one-off flow over time, which is why we built it against real DB records and per-org keys rather than hardcoding values.

---

## Docs Updated

| File | Changes |
|------|---------|
| `service-engine-x-api/docs/INFRASTRUCTURE.md` | Removed Documenso as active, noted per-org Stripe keys, updated endpoint counts |
| `service-engine-x-api/docs/TAXONOMY.md` | Added Stripe fields to Organization/Order, updated proposal flow |
| `service-engine-x-api/update.md` | Added 2026-04-07 changelog, updated migration order |
| `.context/proposal-api-integration-reference.md` | Full integration reference with all endpoints, types, flows, dead code notes |

---

## PRs Merged

- bencrane/service-engine-x#1 — Add Stripe Elements support and per-org publishable key (squash merged to main)
- bencrane/service-engine-x#2 — Update docs for Stripe Elements and per-org keys (squash merged to main)

---

## What's NOT Done Yet

1. **Proposal record for Rare Structure** — needs to be inserted into Supabase with items summing to $27,500
2. **Frontend proposal page** — being built in a separate app (not this repo)
3. **Signing link domain** — hardcoded to `revenueactivation.com/p/{id}` in the create endpoint; needs updating if using `outboundsolutions.com/p/{id}`
4. **ACH details in signed email** — hardcoded to Modern Full, LLC bank details in `resend_service.py`; wrong for Outbound Solutions
5. **Documenso cleanup** — dead code still in codebase (config vars, `upload_to_documenso()` function, DB columns)
6. **`POST /api/proposals/{id}/send` cleanup** — dead endpoint, unreachable
7. **`payment_intent.succeeded` webhook** — works but doesn't create any downstream records (order, engagement, etc.) since the one-off flow doesn't need them
8. **Draft state** — no save-as-draft flow exists if that's ever wanted
