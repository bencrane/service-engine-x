# Service Engine X API - Change Log

## Recent Updates

| Date | Change | Documentation |
|------|--------|---------------|
| 2026-02-13 | Account/Contact Model Migration | [update-accounts-contacts.md](./update-accounts-contacts.md) |
| 2026-02-12 | Systems API & Internal Admin | See below |
| 2026-02-12 | Notification Email Support | See below |
| 2026-02-11 | Stripe Checkout Integration | See below |

---

## 2026-02-13: Account/Contact Model Migration

Implements Salesforce-style Account/Contact model to separate CRM data from auth data. See [update-accounts-contacts.md](./update-accounts-contacts.md) for full details.

**Key changes:**
- New `accounts` and `contacts` tables
- New `/api/accounts` and `/api/contacts` endpoints
- Proposal signing now creates accounts and contacts (dual-write)
- Engagements support both `client_id` and `account_id`

---

## 2026-02-12: Systems API & Internal Admin

Added support for "Systems" (Everything Automation integration) and internal admin endpoints.

### Files Created

**`migrations/005_add_systems.sql`**
- Creates `systems` table for tracking client systems
- Fields: name, type, org_id, user_id, metadata, status

**`app/models/systems.py`**
- Pydantic models for systems CRUD

**`app/routers/systems.py`**
- `GET /api/systems` - List systems
- `POST /api/systems` - Create system
- `GET /api/systems/{id}` - Retrieve system
- `PUT /api/systems/{id}` - Update system
- `DELETE /api/systems/{id}` - Delete system

**`app/routers/internal.py`**
- `POST /api/internal/organizations` - Create organization (admin)
- `GET /api/internal/organizations/{slug}` - Get org by slug
- `GET /api/public/organizations/{slug}/systems` - Public systems list

### Recent Commits
- `3e7a7c9` Add simple login endpoint for testing system access
- `8330b65` Add public endpoint for listing systems by org slug
- `f6eb87e` Add systems API and internal admin endpoints

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
   - Events: `checkout.session.completed`
4. Store webhook secret in `organizations.stripe_webhook_secret`

---

## Migration Order

When setting up a new environment, run migrations in order:

```bash
psql -f migrations/002_add_engagement_model.sql
psql -f migrations/003_conversations_project_scoped.sql
psql -f migrations/004_add_stripe_fields.sql
psql -f migrations/005_add_notification_email.sql
psql -f migrations/005b_add_systems.sql
psql -f migrations/006_add_accounts_contacts.sql
# After dual-write is running:
psql -f migrations/007_migrate_clients_to_accounts.sql
```
