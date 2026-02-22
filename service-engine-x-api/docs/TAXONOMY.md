# Service Engine X: Entity Taxonomy

**Last Updated:** 2026-02-22
**Status:** Living document

This document defines every entity in the Service Engine X platform and clarifies their relationships.

---

## Quick Reference

| Entity | What It Is | Created From | Contains |
|--------|-----------|--------------|----------|
| **Organization** | Your business | Manual setup | Everything |
| **Account** | Client company (CRM) | Proposal signing or manual | Contacts, Engagements |
| **Contact** | Person at company | Proposal signing or manual | Can become User |
| **User** | Login credential | Contact grant or manual | Portal access |
| **Service** | Pricing template | Manual | Used in Proposal Items |
| **Proposal** | Quote/estimate | Manual or API | Proposal Items |
| **Proposal Item** | Line item on quote | Proposal creation | Becomes Project |
| **Engagement** | Work relationship | Proposal signing | Projects, Conversations |
| **Project** | Deliverable with phases | Proposal signing | — |
| **Order** | Financial transaction | Proposal signing | — |

---

## 1. Organization

**What it is:** Your business entity. The top-level tenant in the multi-tenant architecture.

**Key fields:**
- `id` - UUID
- `name` - Business name (e.g., "Revenue Activation")
- `slug` - URL-safe identifier (e.g., "revenue-activation")
- `domain` - Primary domain (e.g., "revenueactivation.com")
- `notification_email` - Where to send system notifications
- `stripe_secret_key` - For payment processing

**Relationships:**
- Owns all other entities via `org_id` foreign key

---

## 2. Account

**What it is:** A client company in the CRM. Follows Salesforce-style model.

**Key fields:**
- `id` - UUID
- `org_id` - Owner organization
- `name` - Company name (e.g., "SecurityPal AI")
- `domain` - Company website domain (e.g., "securitypalhq.com")
- `lifecycle` - Stage in customer journey
- `balance` - Current balance owed
- `total_spent` - Lifetime spend

**Lifecycle values:**
| Value | Meaning |
|-------|---------|
| `lead` | Initial prospect |
| `prospect` | Qualified, in discussion |
| `active` | Paying customer |
| `inactive` | Former customer, dormant |
| `churned` | Lost customer |

**Created by:**
- Manually via API/dashboard
- Automatically when proposal is signed (if account doesn't exist)

**Contains:**
- Contacts (people at this company)
- Engagements (work relationships)
- Orders (transactions)

---

## 3. Contact

**What it is:** A person at an Account. May or may not have portal access.

**Key fields:**
- `id` - UUID
- `org_id` - Owner organization
- `account_id` - Company they belong to (nullable)
- `name_f`, `name_l` - First/last name
- `email` - Email address
- `phone` - Phone number
- `title` - Job title
- `user_id` - If they have portal login (nullable)
- `is_primary` - Primary contact for account
- `is_billing` - Billing contact

**Created by:**
- Manually via API/dashboard
- Automatically when proposal is signed

**Can become:**
- A User (via "Grant Portal Access" action)

---

## 4. User

**What it is:** A login credential. Can be a team member OR a client with portal access.

**Key fields:**
- `id` - UUID
- `org_id` - Owner organization
- `email` - Login email
- `password_hash` - Hashed password (bcrypt)
- `name_f`, `name_l` - First/last name
- `company` - Company name (denormalized)
- `role_id` - Reference to roles table
- `status` - 0=disabled, 1=active

**User types (determined by role):**
| Role | `dashboard_access` | Purpose |
|------|-------------------|---------|
| Client | 0 | Client portal access only |
| Staff/Admin | 1+ | Dashboard access |

**Created by:**
- Manually for team members
- Automatically when proposal is signed (creates client user)
- Via "Grant Portal Access" on a Contact

---

## 5. Service

**What it is:** A pricing template for work you offer. **Internal use** - not a public catalog.

**Key fields:**
- `id` - UUID
- `org_id` - Owner organization
- `name` - Service name (e.g., "CRM Data Cleaning")
- `description` - What it includes
- `price` - Base price
- `currency` - USD, EUR, etc.
- `recurring` - 0=one-time, 1=recurring subscription, 2=setup+recurring
- `f_price`, `f_period_l`, `f_period_t` - First payment details
- `r_price`, `r_period_l`, `r_period_t` - Recurring payment details
- `public` - Whether shown in service catalog
- `metadata` - Custom key-value pairs

**Used for:**
- Template when creating Proposal Items
- Reference on Projects (optional `service_id`)
- NOT directly purchased - proposals are the sales mechanism

**Relationship to other entities:**
```
Service (template)
    ↓ referenced by
Proposal Item (line item on quote)
    ↓ becomes
Project (actual work being done)
```

---

## 6. Proposal

**What it is:** A quote/estimate sent to a prospective client for signing.

**Key fields:**
- `id` - UUID
- `org_id` - Owner organization
- `client_email` - Recipient's email
- `client_name_f`, `client_name_l` - Recipient's name
- `client_company` - Company name
- `status` - Proposal state (see below)
- `total` - Total amount
- `notes` - Payment terms, etc.
- `pdf_url` - Generated PDF
- `signed_at` - When signed
- `signature_data` - Base64 signature image
- `converted_order_id` - Order created on signing
- `converted_engagement_id` - Engagement created on signing

**Status values:**
| ID | Status | Meaning |
|----|--------|---------|
| 0 | Draft | Not yet sent |
| 1 | Sent | Sent, awaiting signature |
| 2 | Signed | Client signed |
| 3 | Rejected | Client declined |

**Contains:**
- Proposal Items (line items defining scope and pricing)

**Signing flow creates:**
1. Account (if not exists)
2. Contact (if not exists)
3. User (if not exists)
4. Engagement
5. Projects (one per proposal item)
6. Order

---

## 7. Proposal Item

**What it is:** A line item on a Proposal. Defines a specific deliverable with price.

**Key fields:**
- `id` - UUID
- `proposal_id` - Parent proposal
- `name` - Deliverable name (e.g., "CRM Data Audit & Cleanup")
- `description` - Scope description
- `price` - Price for this item
- `service_id` - **Required** reference to Service template

**Becomes:**
- A Project when proposal is signed (inherits `service_id`)

**Example:**
```
Proposal for SecurityPal AI - $13,500
├── Proposal Item: "CRM Data Audit" - $4,500  → becomes Project
├── Proposal Item: "ICP Definition" - $3,500  → becomes Project
└── Proposal Item: "Prospect List Build" - $5,500  → becomes Project
```

---

## 8. Engagement

**What it is:** An active work relationship with a client. The container for Projects.

**Key fields:**
- `id` - UUID
- `org_id` - Owner organization
- `client_id` - User (for portal access)
- `account_id` - Account (company)
- `name` - Display name (e.g., "SecurityPal AI - Revenue Ops Buildout")
- `status` - Engagement state
- `proposal_id` - Originating proposal (if any)
- `closed_at` - When closed

**Status values:**
| ID | Status | Meaning |
|----|--------|---------|
| 1 | Active | Work ongoing |
| 2 | Paused | Temporarily on hold |
| 3 | Closed | Relationship ended |

**Contains:**
- Projects (the actual deliverables)
- Conversations (communication threads)

**Key concept:**
- Engagements stay open while Projects complete
- A client can have multiple Engagements (different scopes of work)
- Engagements link to both User (for portal) AND Account (for CRM)

---

## 9. Project

**What it is:** A discrete deliverable with clear completion. Lives inside an Engagement.

**Key fields:**
- `id` - UUID
- `engagement_id` - Parent engagement
- `org_id` - Owner organization
- `name` - Project name
- `description` - Scope
- `status` - Project state
- `phase` - Current phase
- `service_id` - Service template reference (inherited from proposal item)
- `completed_at` - When completed

**Status values:**
| ID | Status | Meaning |
|----|--------|---------|
| 1 | Active | Work in progress |
| 2 | Paused | Temporarily on hold |
| 3 | Completed | Done |
| 4 | Cancelled | Stopped, not completing |

**Phase values:**
| ID | Phase | Description |
|----|-------|-------------|
| 1 | Kickoff | Initial meeting, requirements |
| 2 | Setup | Environment setup, access |
| 3 | Build | Active development |
| 4 | Testing | QA, review cycles |
| 5 | Deployment | Launch, go-live |
| 6 | Handoff | Documentation, training |

**Key concept:**
- Projects have discrete completion (status=Completed)
- Engagements continue after individual Projects complete
- One Engagement can have multiple active Projects

---

## 10. Order

**What it is:** A financial transaction record. **NOT** for tracking work - that's Engagements/Projects.

**Key fields:**
- `id` - UUID
- `org_id` - Owner organization
- `number` - Human-readable order number (e.g., "A1B2C3D4")
- `user_id` - Client user
- `account_id` - Client company
- `engagement_id` - Work this funds
- `service_id` - Primary service (optional)
- `service_name` - Display name
- `price` - Total amount
- `currency` - USD, etc.
- `status` - Payment/delivery status
- `paid_at` - When paid
- `stripe_checkout_session_id` - Stripe reference

**Status values:**
| ID | Status | Meaning |
|----|--------|---------|
| 0 | Unpaid | Awaiting payment |
| 1 | In Progress | Paid, work ongoing |
| 2 | Completed | Delivered |
| 3 | Cancelled | Cancelled/refunded |
| 4 | On Hold | Paused |

**Key concept:**
- Orders are **financial records** only
- Work tracking happens in Engagements/Projects
- One Engagement can have multiple Orders (multiple payments)

---

## Entity Relationship Diagram

```
Organization
│
├── Account (client company)
│   │
│   ├── Contact (person)
│   │   └── User (if portal access granted)
│   │
│   ├── Engagement (work relationship)
│   │   ├── Project (deliverable)
│   │   └── Conversation (communication)
│   │
│   └── Order (financial transaction)
│
├── Service (pricing template)
│   └── used by → Proposal Item → becomes → Project
│
├── Proposal (quote)
│   └── Proposal Item (line item)
│
└── User (team members)
```

---

## Common Flows

### 1. New Client via Proposal

```
1. Create Proposal with Items
   └── Each Item references a Service (optional)

2. Send Proposal to client

3. Client signs Proposal
   └── System creates:
       ├── Account (if new company)
       ├── Contact (if new person)
       ├── User (for portal access)
       ├── Engagement
       ├── Projects (one per Item)
       └── Order (unpaid)

4. Client pays via Stripe
   └── Order status → "In Progress"

5. Work proceeds through Project phases
   └── Kickoff → Setup → Build → Testing → Deployment → Handoff

6. Project completes
   └── Status → "Completed"
   └── Engagement stays Active for future work
```

### 2. Manual Client Setup (no Proposal)

```
1. Create Account
   └── "SecurityPal AI" / securitypalhq.com

2. Create Contact
   └── Pukar Hamal / pukar@securitypalhq.com

3. Grant Portal Access
   └── Creates User with password

4. Create Engagement manually
   └── Link to Account

5. Create Projects manually
   └── Link to Engagement
```

---

## Deprecated/Legacy Entities

These exist in the codebase but are being phased out:

| Entity | Replaced By | Notes |
|--------|-------------|-------|
| `tickets` | `conversations` | Support is now engagement-scoped |
| `ticket_messages` | `conversation_messages` | |
| `order_messages` | `conversation_messages` | Order communication → Engagement conversations |
| `order_tasks` | `projects` | Work tracking moved to Projects |

---

## API Field Mappings

The API uses newer terminology while database has some legacy columns:

| API Field | Database Column | Notes |
|-----------|-----------------|-------|
| `account_name` | `client_company` | On proposals |
| `contact_email` | `client_email` | On proposals |
| `contact_name_f` | `client_name_f` | On proposals |
| `contact_name_l` | `client_name_l` | On proposals |

---

## Status Reference

### Universal Status Meanings

| Status | Active Work | Payment | Relationship |
|--------|-------------|---------|--------------|
| **Draft** | Not started | — | — |
| **Active/In Progress** | Yes | Paid | Ongoing |
| **Paused/On Hold** | Stopped temporarily | Partial? | Ongoing |
| **Completed** | Done | Paid | — |
| **Cancelled** | Stopped | Refunded? | Ended |
| **Closed** | — | — | Ended |
