# Account/Contact Model Migration

## Overview

Implements a Salesforce-style Account/Contact model to separate CRM data from auth data:

- **Account** = company (e.g., "Greenfield Partners") with lifecycle status
- **Contact** = person at account (e.g., "Sarah Chen"), optionally linked to a User for portal access
- **User** = people who can log in (team members + contacts with portal access)

This separates the concept of "client" (a person who signed a proposal) from "account" (the company relationship) and "contact" (individuals at that company).

## Files Created

### `migrations/006_add_accounts_contacts.sql`

Creates the new tables and adds `account_id` to existing tables:

**accounts table:**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| org_id | UUID | Organization reference |
| name | VARCHAR(255) | Company name |
| domain | VARCHAR(255) | Website domain (for matching) |
| lifecycle | VARCHAR(20) | lead, active, inactive, churned |
| balance | DECIMAL(12,2) | Account balance |
| total_spent | DECIMAL(12,2) | Lifetime spend |
| stripe_customer_id | VARCHAR(255) | Stripe customer ID |
| tax_id | VARCHAR(50) | Tax ID |
| aff_id | INTEGER | Affiliate ID |
| aff_link | VARCHAR(255) | Affiliate link |
| source | VARCHAR(50) | Lead source |
| ga_cid | VARCHAR(100) | Google Analytics client ID |
| custom_fields | JSONB | Custom fields |
| note | TEXT | Notes |
| billing_address_id | UUID | Address reference |

**contacts table:**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| org_id | UUID | Organization reference |
| account_id | UUID | Account reference (nullable) |
| name_f | VARCHAR(100) | First name |
| name_l | VARCHAR(100) | Last name |
| email | VARCHAR(255) | Email (unique per org) |
| phone | VARCHAR(50) | Phone |
| title | VARCHAR(100) | Job title |
| user_id | UUID | User reference (if has portal access) |
| is_primary | BOOLEAN | Primary contact flag |
| is_billing | BOOLEAN | Billing contact flag |
| optin | VARCHAR(20) | Marketing opt-in status |
| custom_fields | JSONB | Custom fields |

**Columns added to existing tables:**
- `engagements.account_id` - Links engagement to account
- `orders.account_id` - Links order to account
- `invoices.account_id` - Links invoice to account
- `tickets.account_id` - Links ticket to account
- `proposals.account_id` - Links proposal to account (for lead tracking)

### `migrations/007_migrate_clients_to_accounts.sql`

Backfill migration that:
1. Creates accounts from existing clients (grouped by company name)
2. Creates contacts linked to those accounts
3. Populates `account_id` on existing engagements, orders, invoices, tickets, proposals
4. Includes verification queries to run post-migration

### `app/models/accounts.py`

Pydantic models for accounts:
- `AccountCreate` - Create request body
- `AccountUpdate` - Update request body
- `AccountResponse` - Single account response
- `AccountListResponse` - Account in list response
- `AccountWithContacts` - Account with nested contacts

Lifecycle constants:
- `ACCOUNT_LIFECYCLE_LEAD` = "lead"
- `ACCOUNT_LIFECYCLE_ACTIVE` = "active"
- `ACCOUNT_LIFECYCLE_INACTIVE` = "inactive"
- `ACCOUNT_LIFECYCLE_CHURNED` = "churned"

### `app/models/contacts.py`

Pydantic models for contacts:
- `ContactCreate` - Create request body
- `ContactUpdate` - Update request body
- `ContactResponse` - Single contact response
- `ContactListResponse` - Contact in list response
- `GrantPortalAccessRequest` - Portal access request body

### `app/routers/accounts.py`

New endpoints:
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/accounts` | List accounts (paginated, filterable by lifecycle) |
| POST | `/api/accounts` | Create account |
| GET | `/api/accounts/{id}` | Retrieve account with contacts |
| PUT | `/api/accounts/{id}` | Update account |
| DELETE | `/api/accounts/{id}` | Soft delete account |
| GET | `/api/accounts/{id}/contacts` | List account's contacts |
| GET | `/api/accounts/{id}/engagements` | List account's engagements |

### `app/routers/contacts.py`

New endpoints:
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/contacts` | List contacts (filterable by account, portal access) |
| POST | `/api/contacts` | Create contact |
| GET | `/api/contacts/{id}` | Retrieve contact |
| PUT | `/api/contacts/{id}` | Update contact |
| DELETE | `/api/contacts/{id}` | Soft delete contact |
| POST | `/api/contacts/{id}/grant-portal-access` | Grant portal access (creates user) |

## Files Modified

### `app/routers/proposals.py`

Updated `public_sign_proposal` to implement dual-write:

1. **Find or create Account** (by company name or email domain)
2. **Find or create Contact** (by email, linked to account)
3. **Set lifecycle to "active"** when proposal is signed
4. **Write `account_id`** to engagement, order, and proposal
5. **Link contact to user** if user is created

New response fields:
```json
{
  "success": true,
  "signed_at": "2026-02-13T12:00:00Z",
  "proposal_id": "uuid",
  "account_id": "uuid",    // NEW
  "contact_id": "uuid",    // NEW
  "engagement_id": "uuid",
  "order_id": "uuid",
  "checkout_url": "https://...",
  "signed_pdf_url": "https://...",
  "projects": [...]
}
```

### `app/models/engagements.py`

- Added `AccountSummary` model
- Added `account_id` and `account` fields to `EngagementResponse` and `EngagementListResponse`
- Made `client_id` optional in `EngagementCreate` (can now use `account_id` instead)

### `app/routers/engagements.py`

- Added `account_id` filter parameter to list endpoint
- Updated queries to join with accounts table
- Updated create/retrieve/update to support both `client_id` and `account_id`
- Updated serialization to include account data

### `app/routers/__init__.py`

Added exports:
- `accounts_router`
- `contacts_router`

### `app/models/__init__.py`

Added exports for all new models.

### `app/main.py`

- Registered `accounts_router` and `contacts_router`
- Added `/api/accounts` and `/api/contacts` to API index

## Migration Phases

### Phase 1: Schema (Non-breaking) - COMPLETE
Run `migrations/006_add_accounts_contacts.sql` to create tables and add columns.

### Phase 2: Dual-Write - COMPLETE
Deploy updated application code. New proposal signings will:
- Create accounts and contacts
- Write to both `client_id` and `account_id`
- Keep reads from old columns

### Phase 3: Data Backfill
Run `migrations/007_migrate_clients_to_accounts.sql` to:
- Migrate existing clients to accounts + contacts
- Populate `account_id` on historical records

### Phase 4: Switch Reads (Future)
- Update routers to read from `account_id`
- Deprecate `client_id` in responses
- Update `/api/clients` to wrap accounts/contacts

### Phase 5: Cleanup (Future)
- Remove dual-write
- Make `account_id` NOT NULL
- Eventually drop `client_id`

## Setup Steps

1. Run schema migration:
   ```bash
   psql -f migrations/006_add_accounts_contacts.sql
   ```

2. Deploy application code

3. Run backfill migration (after some dual-write data accumulates):
   ```bash
   psql -f migrations/007_migrate_clients_to_accounts.sql
   ```

4. Verify with queries in migration file

## Key Design Decisions

- **Dual-write during transition**: Both `client_id` and `account_id` are written to allow gradual migration
- **Account matching by domain**: Email domains (excluding gmail, yahoo, etc.) are used to match existing accounts
- **Contact linked to user**: When a contact gets portal access, they're linked to a user record
- **Lifecycle tracking**: Accounts have lifecycle status (lead -> active -> inactive -> churned)
- **Primary/billing flags**: Contacts can be marked as primary or billing contact for an account

## API Examples

### Create Account
```bash
curl -X POST /api/accounts \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Acme Corp", "domain": "acme.com", "lifecycle": "lead"}'
```

### Create Contact
```bash
curl -X POST /api/contacts \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "account_id": "uuid",
    "name_f": "John",
    "name_l": "Doe",
    "email": "john@acme.com",
    "is_primary": true
  }'
```

### Grant Portal Access
```bash
curl -X POST /api/contacts/{id}/grant-portal-access \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"send_welcome_email": true}'
```

### Create Engagement with Account
```bash
curl -X POST /api/engagements \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"account_id": "uuid", "name": "Website Redesign"}'
```
