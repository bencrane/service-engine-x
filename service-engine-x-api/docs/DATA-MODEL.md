# Data Model: Accounts, Contacts & Related Entities

## Overview

This follows a Salesforce-style CRM model:

- **Account** = A company (e.g., "Greenfield Partners")
- **Contact** = A person at a company (e.g., "Sarah Chen")
- **User** = Someone who can log in (team members OR contacts with portal access)

---

## Core Entities

### Account
A company/organization that is a client or prospect.

| Field | Description |
|-------|-------------|
| `id` | UUID |
| `org_id` | Which org owns this account |
| `name` | Company name |
| `domain` | Website domain (e.g., "greenfield.com") |
| `lifecycle` | `lead` → `active` → `inactive` → `churned` |
| `balance` | Current balance owed |
| `total_spent` | Lifetime spend |
| `stripe_customer_id` | Stripe reference |

### Contact
A person, usually associated with an Account.

| Field | Description |
|-------|-------------|
| `id` | UUID |
| `org_id` | Which org owns this contact |
| `account_id` | Which Account they belong to (nullable) |
| `name_f`, `name_l` | First/last name |
| `email` | Email address |
| `phone` | Phone number |
| `title` | Job title |
| `user_id` | If they have portal login access |
| `is_primary` | Primary contact for the account |
| `is_billing` | Billing contact |

### User
Someone who can log in to the system.

| Field | Description |
|-------|-------------|
| `id` | UUID |
| `email` | Login email |
| `password_hash` | Hashed password |
| `dashboard_access` | 0 = client, 1+ = team member |

---

## Relationship Diagram

```
Organization (your business)
    │
    ├── Account (client company)
    │       │
    │       ├── Contact (person at company)
    │       │       └── User (if they have portal access)
    │       │
    │       ├── Engagement (ongoing work relationship)
    │       │       └── Project (specific deliverable)
    │       │
    │       ├── Order (one-time purchase)
    │       │
    │       ├── Invoice
    │       │
    │       └── Proposal (sent to contact)
    │
    └── User (your team members)
```

---

## Proposals

A proposal is sent to a **Contact** at an **Account** (or a standalone contact).

| Field | Description |
|-------|-------------|
| `id` | UUID |
| `org_id` | Your organization |
| `client_email` | Contact's email |
| `client_name_f`, `client_name_l` | Contact's name |
| `client_company` | Account name (denormalized) |
| `account_id` | FK to Account (if linked) |
| `status` | 0=Draft, 1=Sent, 2=Signed, 3=Rejected |
| `total` | Total amount |
| `items` | Line items (via `proposal_items` table) |

### Proposal Flow
1. **Create** → status = Draft (0) or Sent (1)
2. **Send** → Email goes to contact with signing link
3. **Sign** → Contact signs at `/p/{proposal_id}`
4. **Convert** → Creates Engagement + Order + User (if needed)

---

## Engagements & Projects

An **Engagement** is an ongoing client relationship. It contains **Projects**.

```
Engagement (e.g., "2024 Marketing Retainer")
    ├── Project (e.g., "Website Redesign")
    ├── Project (e.g., "SEO Optimization")
    └── Project (e.g., "Content Strategy")
```

| Engagement Fields | Description |
|-------------------|-------------|
| `account_id` | Which Account |
| `status` | active, completed, cancelled |
| `start_date`, `end_date` | Timeline |

| Project Fields | Description |
|----------------|-------------|
| `engagement_id` | Parent engagement |
| `name` | Project name |
| `status` | Status |
| `budget` | Project budget |

---

## Orders

A one-time purchase or payment.

| Field | Description |
|-------|-------------|
| `id` | UUID |
| `org_id` | Your organization |
| `user_id` | The client user |
| `account_id` | The Account (if linked) |
| `status` | 0=Unpaid, 1=In Progress, 2=Completed, 3=Cancelled |
| `total` | Amount |

---

## Current State (Migration in Progress)

The codebase is transitioning from a simpler model to the Account/Contact model:

### Old Model (still in database)
- `proposals.client_email`, `client_name_f`, `client_name_l`, `client_company`
- `orders.user_id` (client was a User)

### New Model (being added)
- `accounts` table
- `contacts` table
- `proposals.account_id` (FK to Account)
- `engagements.account_id` (FK to Account)

### API Field Mapping
The API uses the new terminology, but maps to old database columns:

| API Field | Database Column |
|-----------|-----------------|
| `account_name` | `client_company` |
| `contact_email` | `client_email` |
| `contact_name_f` | `client_name_f` |
| `contact_name_l` | `client_name_l` |

---

## Summary

| Entity | What it represents | Key relationships |
|--------|-------------------|-------------------|
| **Organization** | Your business | Owns everything |
| **Account** | Client company | Has Contacts, Engagements, Orders |
| **Contact** | Person at Account | Can become a User |
| **User** | Login credential | Team member or client with access |
| **Proposal** | Quote/estimate | Sent to Contact, converts to Engagement |
| **Engagement** | Client relationship | Contains Projects |
| **Project** | Specific work | Belongs to Engagement |
| **Order** | One-time purchase | Linked to Account/User |
