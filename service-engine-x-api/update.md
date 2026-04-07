# Service Engine X API - Change Log

**Last Updated:** 2026-04-07

## Recent Updates

| Date | Change | Documentation |
|------|--------|---------------|
| 2026-04-07 | Stripe Elements + per-org publishable key | See below |
| 2026-02-13 | Account/Contact Model Migration | [update-accounts-contacts.md](./update-accounts-contacts.md) |
| 2026-02-12 | Notification Email Support | See below |
| 2026-02-11 | Stripe Checkout Integration | See below |

---

## 2026-04-07: Stripe Elements Support & Per-Org Publishable Key

Added Stripe Elements (PaymentIntent) flow alongside existing Checkout flow. Stripe keys are per-org in the database, not app-level env vars.

### Migration

**`migrations/009_add_stripe_publishable_key.sql`**
- Adds `organizations.stripe_publishable_key` column

### New Endpoints

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| `POST` | `/api/public/proposals/{id}/payment-intent` | None | Create PaymentIntent for Stripe Elements |
| `POST` | `/api/public/proposals/{id}/checkout` | None | Create Checkout session (redirect flow) |

### Changes to Existing Endpoints

**`GET /api/public/proposals/{id}`** — now returns `org_slug`, `org_domain`, `stripe_publishable_key`

**`POST /api/webhooks/stripe`** — now handles `payment_intent.succeeded` in addition to `checkout.session.completed`

### Frontend Payment Flow (Stripe Elements)

```
1. GET /api/public/proposals/{id} → get stripe_publishable_key
2. Initialize Stripe(publishableKey), mount Payment Element
3. POST /api/public/proposals/{id}/payment-intent → get client_secret
4. stripe.confirmPayment({ clientSecret, elements })
5. Webhook receives payment_intent.succeeded
```

### Key Design Decisions

- **Per-org Stripe keys**: `stripe_secret_key`, `stripe_publishable_key`, `stripe_webhook_secret` all stored on `organizations` table
- **Restricted keys supported**: `rk_live_...` keys work as drop-in replacement for `sk_live_...`
- **Documenso is dead code**: The only code path calling Documenso (`POST /send`) requires status=0 (Draft), but Create sets status=1 (Sent) — unreachable

### Setup

```bash
psql -f migrations/009_add_stripe_publishable_key.sql
```

```sql
UPDATE organizations
SET stripe_secret_key      = 'rk_live_...',
    stripe_publishable_key = 'pk_live_...',
    stripe_webhook_secret  = 'whsec_...',
    updated_at             = now()
WHERE slug = 'outbound-solutions';
```

Add `payment_intent.succeeded` event to your Stripe webhook destination in the Stripe dashboard.

---

## 2026-02-13: Account/Contact Model Migration

Implements Salesforce-style Account/Contact model to separate CRM data from auth data. See [update-accounts-contacts.md](./update-accounts-contacts.md) for full details.

**Key changes:**
- New `accounts` and `contacts` tables
- New `/api/accounts` and `/api/contacts` endpoints
- Proposal signing now creates accounts and contacts (dual-write)
- Engagements support both `client_id` and `account_id`

---

## 2026-02-12: Notification Email Support

Added notification email field to organizations for proposal signing alerts.

### Files Created

**`migrations/005_add_notification_email.sql`**
- Adds `organizations.notification_email` column
- Seeds values for existing organizations

### Changes
- Proposal signed emails now CC the organization's notification email
- ACH payment details included in signed proposal emails

### Recent Commits
- `9f873d3` Update email to include ACH payment details
- `ecdcf47` Add logging for PDF generation errors

---

## 2026-02-11: Stripe Checkout Integration

After a proposal is signed via `public_sign_proposal`, the API creates a Stripe Checkout session with itemized line items and returns `checkout_url` for frontend redirect.

### Files Created

**`migrations/004_add_stripe_fields.sql`**

Database migration that adds:
- `organizations.domain` - For success/cancel redirect URLs
- `organizations.stripe_webhook_secret` - For verifying webhook events
- `orders.stripe_checkout_session_id` - Tracks the Stripe session
- `orders.stripe_payment_intent_id` - Stored after successful payment
- `orders.paid_at` - Timestamp when payment completed

Seeds domain values:
| Organization | Domain |
|--------------|--------|
| Revenue Activation | revenueactivation.com |
| Everything Automation | everythingautomation.com |
| Outbound Solutions | outboundsolutions.com |

**`app/services/stripe_service.py`**

Stripe integration service with three functions:
- `create_checkout_session()` - Creates a Stripe Checkout session
- `build_line_items_from_proposal()` - Converts proposal items to Stripe format
- `verify_webhook_signature()` - Verifies webhook signatures

### Files Modified

**`requirements.txt`**
```
stripe>=7.0.0
```

**`app/routers/proposals.py`**
1. Stripe Checkout creation in `public_sign_proposal`
2. New webhook endpoint `POST /api/webhooks/stripe`

### Response from `public_sign_proposal`

```json
{
  "success": true,
  "signed_at": "2026-02-11T12:00:00Z",
  "proposal_id": "uuid",
  "account_id": "uuid",
  "contact_id": "uuid",
  "engagement_id": "uuid",
  "order_id": "uuid",
  "checkout_url": "https://checkout.stripe.com/c/pay/...",
  "signed_pdf_url": "https://...",
  "projects": [{"id": "uuid", "name": "Project Name"}]
}
```

### Key Design Decisions

- **Graceful failure**: Signing succeeds even if Stripe fails; `checkout_url` will be null
- **Itemized line items**: One line item per proposal item (not single total)
- **Per-org Stripe keys**: Uses `organizations.stripe_secret_key`
- **Optional webhook verification**: Only verifies if `stripe_webhook_secret` is set

### Frontend Flow

1. Call `POST /api/public/proposals/{id}/sign`
2. Show "Signed!" confirmation
3. If `checkout_url` present: `window.location.href = checkout_url`
4. Stripe handles payment
5. Redirects to org domain with `?payment=success&order_id={id}`

### Setup Steps

1. Run migration: `psql -f migrations/004_add_stripe_fields.sql`
2. Install stripe: `pip install stripe>=7.0.0`
3. Configure Stripe webhook in dashboard:
   - URL: `https://api.serviceengine.xyz/api/webhooks/stripe`
   - Events: `checkout.session.completed`, `payment_intent.succeeded`
4. Store webhook secret in `organizations.stripe_webhook_secret`

---

## Migration Order

When setting up a new environment, run migrations in order:

```bash
psql -f migrations/002_add_engagement_model.sql
psql -f migrations/003_conversations_project_scoped.sql
psql -f migrations/004_add_stripe_fields.sql
psql -f migrations/005_add_notification_email.sql
psql -f migrations/006_add_accounts_contacts.sql
# After dual-write is running:
psql -f migrations/007_migrate_clients_to_accounts.sql
psql -f migrations/008_drop_systems.sql
psql -f migrations/009_add_stripe_publishable_key.sql
```
