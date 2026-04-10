# Meetings & Deals: Implementation Proposal

## Status

**Proposed** — not yet implemented. This document captures the agreed-upon design for adding meetings and deals to Service Engine X.

---

## Background

Service Engine X (SERX) currently has no pre-proposal pipeline. The entity chain starts at proposals:

```
Proposal → Engagement → Project → Order
```

There is no way to track: someone booked a call → we met → we qualified them → we sent a proposal. The pipeline starts at proposal creation.

Previously, booking and deal data lived in a separate Outbound Supabase database with its own `companies`, `people`, `bookings`, and `deals` tables. We are consolidating into SERX as the single system of record.

### What exists today in SERX

| Table | Purpose |
|-------|---------|
| `organizations` | Tenant root. All data scoped by `org_id`. |
| `accounts` | Companies/clients. Has `name`, `domain`, `lifecycle` (lead/active/inactive/churned), `source`. |
| `contacts` | People at accounts. Has `name_f`, `name_l`, `email`, `phone`, `title`. Unique on `(org_id, email)`. |
| `proposals` | Quotes. Status: Draft → Sent → Signed → Rejected. Signing creates Engagement + Order. |
| `engagements` | Active client relationships. Contains projects. Has `proposal_id` (originating proposal). |
| `projects` | Deliverables under an engagement. |
| `orders` | Payments. Linked to engagement and account. |
| `cal_team_mappings` | Maps SERX org to Cal.com team (by `cal_team_id`). |
| `cal_team_members` | Members of Cal.com teams. |
| `calcom_webhook_log` | Raw webhook payload capture (debug/dev table). |

### What we are adding

Two new tables: `meetings` and `deals`. These sit upstream of proposals in the pipeline:

```
Cal.com booking event → meeting → deal → proposal → engagement → project → order
```

---

## Core Concepts

### Meetings are not deals

A meeting is a factual record: a calendar event happened (or is scheduled to happen). A deal is a judgment: this prospect is a qualified sales opportunity.

- A meeting can exist without a deal indefinitely.
- A deal is only created when a meeting (or prospect) is explicitly qualified.
- A deal can have multiple meetings (initial call, follow-up, proposal walkthrough).

### The flow

```
1. Cal.com BOOKING_CREATED webhook fires
       ↓
2. cal_booking_events row created (always, unconditionally — separate concern)
       ↓
3. Intake agent evaluates:
   - Business email domain? → find/create account + contact
   - Internal/non-sales? → stop here, no meeting record
       ↓
4. Meeting created (status: scheduled)
   - account_id and contact_id set
   - cal_event_uid links back to cal_booking_events
   - deal_id = NULL (always null at creation)
       ↓
5. MEETING_ENDED webhook fires → meeting.status → completed
       ↓
6. Intake agent or human qualifies the meeting
   - Deal created (status: qualified, source: "cal.com")
   - meeting.deal_id set to new deal
   - Future meetings with same prospect linked to this deal explicitly
       ↓
7. Proposal generated and linked → deal.proposal_id set, deal.status → proposal_sent
       ↓
8. Proposal signed (existing SERX flow, unchanged)
   - Engagement created (proposal.converted_engagement_id)
   - Order created (proposal.converted_order_id)
   - deal.status → won, deal.closed_at set
   - account.lifecycle → active
```

### Why deal_id is never auto-set on meeting creation

Auto-linking a meeting to a deal by account alone is unreliable:
- The same account can have multiple deals (different contacts, different services, a past won deal and a new opportunity).
- Matching on account + contact is better but still not airtight (same contact, new opportunity).

The meeting is a fact. The deal association is a judgment call. An intake agent or human links them explicitly.

---

## Schema

### `meetings` table

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | |
| `org_id` | UUID | NOT NULL, FK → organizations(id) | Multi-tenant scope |
| `account_id` | UUID | FK → accounts(id), nullable | Company — nullable for internal/unlinked meetings |
| `contact_id` | UUID | FK → contacts(id), nullable | Person — nullable for same reason |
| `deal_id` | UUID | FK → deals(id), nullable | Set explicitly when qualified, not at creation |
| `cal_event_uid` | VARCHAR(255) | UNIQUE, nullable | Links to cal_booking_events. Null if manually created. |
| `title` | VARCHAR(255) | NOT NULL | Meeting title |
| `start_time` | TIMESTAMPTZ | NOT NULL | |
| `end_time` | TIMESTAMPTZ | NOT NULL | |
| `status` | VARCHAR(20) | NOT NULL DEFAULT 'scheduled' | scheduled, completed, cancelled, no_show, rescheduled |
| `organizer_email` | VARCHAR(255) | nullable | Team member's calendar |
| `attendee_emails` | JSONB | DEFAULT '[]' | Array of attendee email strings |
| `notes` | TEXT | nullable | Post-meeting notes |
| `created_at` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |

**Design decisions:**
- No soft delete. Meetings are factual records. If cancelled, `status` = `cancelled`.
- `cal_event_uid` is nullable to support manually-created meetings not originating from Cal.com.
- `cal_event_uid` is UNIQUE to prevent duplicate imports and allow lookup from Cal.com event UID.

### `deals` table

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | |
| `org_id` | UUID | NOT NULL, FK → organizations(id) | Multi-tenant scope |
| `account_id` | UUID | FK → accounts(id), nullable | Company being sold to |
| `contact_id` | UUID | FK → contacts(id), nullable | Primary contact for this deal |
| `proposal_id` | UUID | FK → proposals(id), nullable | Set when proposal is generated |
| `title` | VARCHAR(255) | NOT NULL | e.g. "Outbound campaign for Acme" |
| `status` | VARCHAR(20) | NOT NULL DEFAULT 'qualified' | qualified, proposal_sent, negotiating, won, lost |
| `value` | DECIMAL(12,2) | nullable | Estimated deal value |
| `source` | VARCHAR(50) | nullable | "cal.com", "manual", "referral" |
| `referred_by_account_id` | UUID | FK → accounts(id), nullable | Partner/referral source |
| `lost_reason` | TEXT | nullable | Populated when status = lost |
| `notes` | TEXT | nullable | |
| `created_at` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| `closed_at` | TIMESTAMPTZ | nullable | Set when status → won or lost |
| `deleted_at` | TIMESTAMPTZ | nullable | Soft delete, following SERX pattern |

**Design decisions:**
- No `new` or `met` status. Those are meeting-level concepts. A deal starts at `qualified`.
- No `unqualified` status. If a meeting isn't qualified, no deal is created.
- `account_id` and `contact_id` are nullable but should realistically always be populated by the time a deal is created (the intake agent creates them at meeting time).
- Deals own the link to proposals (`deal.proposal_id`). There is no reverse `deal_id` on the proposals table. Single direction of ownership.

---

## Entity Relationships

```
Organization (tenant root)
├── Account (company)
│   └── Contact (person)
│
├── Meeting (calendar event)
│   ├── account_id → Account (nullable)
│   ├── contact_id → Contact (nullable)
│   ├── deal_id → Deal (nullable, set on qualification)
│   └── cal_event_uid → cal_booking_events (traceability)
│
├── Deal (sales opportunity, created on qualification)
│   ├── account_id → Account
│   ├── contact_id → Contact
│   ├── proposal_id → Proposal (nullable, set when proposal generated)
│   ├── referred_by_account_id → Account (nullable)
│   └── ← meetings (one deal has many meetings)
│
├── Proposal (quote — existing)
│   └── converted_engagement_id → Engagement (set on signing — existing)
│
├── Engagement (active contract — existing)
│   └── Project (deliverable — existing)
│
└── Order (payment — existing)
```

### When a deal is won

1. The proposal signing flow already creates an Engagement + Order — that does not change.
2. `deal.proposal_id` links to the proposal. `proposal.converted_engagement_id` links to the engagement. The chain is: `deal → proposal → engagement → projects → orders`. No new FK needed on engagements.
3. `deal.status` → `won`, `deal.closed_at` set.
4. `account.lifecycle` → `active`.

### When a deal is lost

1. `deal.status` → `lost`, `deal.closed_at` set, `deal.lost_reason` populated.
2. Account stays at current lifecycle (typically `lead`).

---

## Migration SQL

```sql
-- 015_add_meetings_and_deals.sql

-- Deals: sales pipeline opportunities, created only when qualified.
CREATE TABLE deals (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id                  UUID NOT NULL REFERENCES organizations(id),
    account_id              UUID REFERENCES accounts(id),
    contact_id              UUID REFERENCES contacts(id),
    proposal_id             UUID REFERENCES proposals(id),
    title                   VARCHAR(255) NOT NULL,
    status                  VARCHAR(20) NOT NULL DEFAULT 'qualified',
    value                   DECIMAL(12,2),
    source                  VARCHAR(50),
    referred_by_account_id  UUID REFERENCES accounts(id),
    lost_reason             TEXT,
    notes                   TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at               TIMESTAMPTZ,
    deleted_at              TIMESTAMPTZ
);

CREATE INDEX idx_deals_org_id ON deals(org_id);
CREATE INDEX idx_deals_account_id ON deals(account_id);
CREATE INDEX idx_deals_contact_id ON deals(contact_id);
CREATE INDEX idx_deals_proposal_id ON deals(proposal_id);
CREATE INDEX idx_deals_status ON deals(status);
CREATE INDEX idx_deals_source ON deals(source);
CREATE INDEX idx_deals_deleted_at ON deals(deleted_at) WHERE deleted_at IS NULL;

COMMENT ON TABLE deals IS 'Sales pipeline opportunities. Created when a meeting is qualified. Tracks through proposal to won/lost.';

-- Meetings: calendar events, optionally associated with a deal.
-- deals must be created first because meetings.deal_id references deals(id).
CREATE TABLE meetings (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id              UUID NOT NULL REFERENCES organizations(id),
    account_id          UUID REFERENCES accounts(id),
    contact_id          UUID REFERENCES contacts(id),
    deal_id             UUID REFERENCES deals(id),
    cal_event_uid       VARCHAR(255) UNIQUE,
    title               VARCHAR(255) NOT NULL,
    start_time          TIMESTAMPTZ NOT NULL,
    end_time            TIMESTAMPTZ NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    organizer_email     VARCHAR(255),
    attendee_emails     JSONB DEFAULT '[]',
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_meetings_org_id ON meetings(org_id);
CREATE INDEX idx_meetings_deal_id ON meetings(deal_id);
CREATE INDEX idx_meetings_account_id ON meetings(account_id);
CREATE INDEX idx_meetings_contact_id ON meetings(contact_id);
CREATE INDEX idx_meetings_status ON meetings(status);

COMMENT ON TABLE meetings IS 'Calendar meetings with prospects. Optionally linked to a deal when qualified.';
```

**Notes:**
- `deals` is created before `meetings` because `meetings.deal_id` references `deals(id)`.
- No ALTER TABLE on proposals. The deal owns the link via `deal.proposal_id`.
- No `cal_booking_events` table in this migration. That table is part of a separate Cal.com data normalization effort and is created/managed independently.

---

## API Endpoints

### Org resolution (internal)

**Resolve org from Cal.com team ID**
```
GET /api/internal/resolve-org?cal_team_id=139009
```
Looks up `cal_team_mappings` by `cal_team_id` → returns org_id, org name, org domain. This is the first call any agent makes when processing a Cal.com webhook. Resolution is via `cal_team_id` (from the webhook payload's team context), not by email domain matching.

### Meeting endpoints (internal, X-Internal-Key)

**Create meeting from Cal.com event**
```
POST /api/internal/orgs/{org_id}/meetings/from-cal-event
```
Request body:
```json
{
  "attendee_name": "Jane Smith",
  "attendee_email": "jane@acme.com",
  "cal_event_uid": "abc-123",
  "title": "Intro Call",
  "start_time": "2026-04-15T10:00:00Z",
  "end_time": "2026-04-15T10:30:00Z",
  "organizer_email": "team@outboundsolutions.com"
}
```
Behavior:
- Finds or creates account by domain (`acme.com` extracted from attendee email)
- Finds or creates contact by email (`jane@acme.com`), splitting name on first space for `name_f`/`name_l`
- Creates meeting with `deal_id = NULL` (always)
- Returns: meeting + account + contact

Account creation from Cal.com payload — field availability:

| Account field | Required? | Available from Cal.com? | Handling |
|---------------|-----------|------------------------|----------|
| `org_id` | NOT NULL | Yes (resolved via cal_team_mappings) | |
| `name` | NOT NULL | No — only have domain | Use domain as placeholder (e.g. "acme.com") |
| `domain` | nullable | Yes — extracted from email | |
| `lifecycle` | default 'lead' | N/A | Use default |
| `source` | nullable | Yes | Set to "cal.com" |

Contact creation from Cal.com payload — field availability:

| Contact field | Required? | Available from Cal.com? | Handling |
|---------------|-----------|------------------------|----------|
| `org_id` | NOT NULL | Yes | |
| `account_id` | nullable | Yes — from the account just found/created | |
| `name_f` | NOT NULL | Partial — full name provided | Split on first space |
| `name_l` | NOT NULL | Partial — full name provided | Everything after first space, or empty string |
| `email` | NOT NULL | Yes | |
| `phone`, `title` | nullable | No | Left null |

**Update meeting**
```
PUT /api/internal/orgs/{org_id}/meetings/{meeting_id}
```
Body: `status`, `deal_id`, `notes`. Used by MEETING_ENDED handler to set `status` → `completed`, and by intake agent to link a meeting to a deal.

**List meetings for an account**
```
GET /api/internal/orgs/{org_id}/accounts/{account_id}/meetings
```
Returns all meetings for an account regardless of deal association.

### Deal endpoints (internal, X-Internal-Key)

**Create deal (qualify a meeting)**
```
POST /api/internal/orgs/{org_id}/deals
```
Request body:
```json
{
  "meeting_id": "...",
  "title": "Outbound campaign for Acme",
  "value": 5000.00,
  "source": "cal.com"
}
```
Behavior:
- Creates deal (copies `account_id` and `contact_id` from the meeting)
- Sets `meeting.deal_id` to the new deal
- Returns: deal + meeting(s)

**Get deal**
```
GET /api/internal/orgs/{org_id}/deals/{deal_id}
```
Returns deal with nested: account, contact, meetings (array), proposal (if linked).

**Update deal**
```
PUT /api/internal/orgs/{org_id}/deals/{deal_id}
```
Body: `status`, `value`, `lost_reason`, `notes`, etc. Auto-sets `closed_at` when status → won or lost. Auto-updates `account.lifecycle` → `active` when status → won.

**Link proposal to deal**
```
PUT /api/internal/orgs/{org_id}/deals/{deal_id}/proposal
```
Body: `{ "proposal_id": "..." }`
Sets `deal.proposal_id`, updates `deal.status` → `proposal_sent`.

**Add booking to existing deal**
```
POST /api/internal/orgs/{org_id}/deals/{deal_id}/meetings
```
For follow-up meetings on the same deal.

### User-facing endpoints (JWT auth, for dashboard)

```
GET    /api/deals              — List deals (paginated, filterable by status)
GET    /api/deals/{id}         — Get deal with meetings, account, contact, proposal
PUT    /api/deals/{id}         — Update deal
DELETE /api/deals/{id}         — Soft delete

GET    /api/meetings           — List meetings (paginated, filterable by status)
GET    /api/meetings/{id}      — Get meeting with account, contact, deal
PUT    /api/meetings/{id}      — Update meeting (notes, status)
```

These follow existing SERX patterns: pagination with `limit`/`page`, sort with `field:direction`, org-scoped via JWT `org_id`.

---

## Implementation Phases

### Phase 1: Schema
- Run migration `015_add_meetings_and_deals.sql` to create both tables.
- No changes to existing tables.

### Phase 2: Internal API (meetings)
- `POST /api/internal/orgs/{org_id}/meetings/from-cal-event` — the main intake endpoint.
- `PUT /api/internal/orgs/{org_id}/meetings/{meeting_id}` — update status/deal_id/notes.
- `GET /api/internal/resolve-org?cal_team_id=...` — org resolution for agents.
- Pydantic models for meeting create/update/response.

### Phase 3: Internal API (deals)
- `POST /api/internal/orgs/{org_id}/deals` — create deal from qualified meeting.
- `GET /api/internal/orgs/{org_id}/deals/{deal_id}` — get deal with related entities.
- `PUT /api/internal/orgs/{org_id}/deals/{deal_id}` — update deal status/fields.
- `PUT /api/internal/orgs/{org_id}/deals/{deal_id}/proposal` — link proposal.
- Pydantic models for deal create/update/response.

### Phase 4: User-facing API
- CRUD endpoints for `/api/deals` and `/api/meetings` with JWT auth.
- Follow existing patterns from accounts/contacts routers.

---

## Conflicts and Flags

**No conflicts with existing schema.** Specific notes:

1. **`proposals.converted_engagement_id`** — exists and handles proposal → engagement. Deals sit upstream and do not interfere.
2. **`engagements.proposal_id`** — exists. The chain `deal → proposal → engagement` works without changes to engagements.
3. **`accounts.source`** — exists as VARCHAR(50). Can be set to `"cal.com"` when auto-created from a Cal.com event. No change needed.
4. **`contacts.name_l` is NOT NULL** — Cal.com may provide a single name with no space. Intake agent should use empty string for `name_l` if no space. No schema change, but worth handling in code.
5. **`CALCOM-DEALS.md`** — documents the old Outbound DB approach. Should be archived or updated once this is implemented, as it describes a system being replaced.

---

## Related Cal.com Tables (context only)

This proposal does not create these tables, but they exist as part of the broader Cal.com data normalization effort:

- `cal_booking_events` — normalized Cal.com booking event records
- `cal_contacts` — Cal.com contact records
- `cal_booking_attendees` — attendees per booking
- `cal_booking_responses` — custom field responses per booking
- `cal_form_submissions` — Cal.com form submissions
- `cal_ooo_entries` — out-of-office entries
- `cal_recordings` — meeting recordings

The `meetings` table links to `cal_booking_events` via `cal_event_uid` for traceability. The `calcom_webhook_log` table (already exists) captures raw webhook payloads for debugging.

---

## Existing Cal.com Infrastructure in SERX

| Table | Purpose | Status |
|-------|---------|--------|
| `cal_team_mappings` | Maps SERX org_id ↔ Cal.com team_id | Live, populated |
| `cal_team_members` | Members of Cal.com teams | Live, populated |
| `calcom_webhook_log` | Raw webhook payload capture | Live, endpoint at POST /api/webhooks/calcom |
