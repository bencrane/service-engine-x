# Cal.com Booking & Deal Logic

## Overview

Cal.com webhooks are processed by a Modal serverless function (`data-enrichment-orchestration-v1/src/calcom_ingest.py`). The system tracks meetings and creates deal records to follow the sales pipeline.

---

## Entities

### Company
A business entity, identified by email domain.

| Field | Description |
|-------|-------------|
| `id` | UUID |
| `name` | Company name (or domain if unknown) |
| `domain` | Email domain (e.g., "acme.com") |

### Person
An individual who books a meeting.

| Field | Description |
|-------|-------------|
| `id` | UUID |
| `email` | Email address |
| `name` | Full name |
| `company_id` | FK to Company (if identifiable) |

### Booking
A scheduled meeting from Cal.com.

| Field | Description |
|-------|-------------|
| `id` | UUID |
| `calcom_uid` | Cal.com's unique booking ID |
| `person_id` | FK to Person |
| `title` | Meeting title |
| `start_time` / `end_time` | Scheduled time |
| `status` | ACCEPTED, CANCELLED |
| `attended` | Boolean - set true after meeting ends |
| `organizer_email` | Team member who owns the calendar |

### Deal
A sales opportunity, tied to a Company.

| Field | Description |
|-------|-------------|
| `id` | UUID |
| `company_id` | FK to Company |
| `status` | `active` or `cancelled` |
| `stage` | `booked` → `met` |

---

## What Creates a Deal?

A deal is created when:

1. **A booking is created** (BOOKING_CREATED webhook)
2. **The attendee's email has a business domain** (not gmail.com, yahoo.com, etc.)
3. **No active deal exists** for that company

### Domain Classification

Personal email domains are **excluded** from company/deal creation:
- gmail.com
- yahoo.com
- hotmail.com
- outlook.com
- icloud.com
- me.com

If someone books with a personal email, a Person record is created but **no Company or Deal**.

---

## Deal Stages

| Stage | Meaning | Triggered By |
|-------|---------|--------------|
| `booked` | Meeting scheduled | BOOKING_CREATED |
| `met` | Meeting completed | MEETING_ENDED |

---

## Event Flow

### BOOKING_CREATED

```
Webhook received
    ↓
Store raw event in calcom_events
    ↓
Find or create Company (by email domain)
    ↓
Find or create Person (by email)
    ↓
Create Booking record
    ↓
If company exists AND no active deal:
    Create Deal (status=active, stage=booked)
    ↓
Send confirmation email to attendee
```

### BOOKING_RESCHEDULED

```
Webhook received
    ↓
Look up original booking by rescheduleUid
    ↓
Update booking with new times and calcom_uid
    ↓
Send reschedule notification email
```

Note: Cal.com creates a **new** booking ID when rescheduling. The original UID is in `rescheduleUid`.

### BOOKING_CANCELLED

```
Webhook received
    ↓
Update booking status to CANCELLED
    ↓
If person has company:
    Cancel active deal (status → cancelled)
    ↓
Send cancellation email
```

### MEETING_ENDED

```
Webhook received
    ↓
Mark booking as attended=true
    ↓
If person has company with active deal:
    Advance deal stage to 'met'
```

---

## Email Routing

Emails are sent from the organizer's domain:

| Organizer Domain | From Email |
|------------------|------------|
| revenueactivation.com | team@revenueactivation.com |
| outboundsolutions.com | team@outboundsolutions.com |
| revenueengineer.com | benjamin.crane@revenueengineer.com |
| modernfull.com | team@modernfull.com |
| everythingautomation.com | team@everythingautomation.com |
| substrate.build | team@substrate.build |
| (default) | team@outboundsolutions.com |

---

## Database Tables

All data is stored in the **Outbound Supabase** database (not Service Engine X).

| Table | Purpose |
|-------|---------|
| `calcom_events` | Raw webhook payloads (audit log) |
| `companies` | Business entities |
| `people` | Individual contacts |
| `bookings` | Meeting records |
| `deals` | Sales opportunities |

---

## Summary

| Action | Creates Deal? | Updates Deal? |
|--------|--------------|---------------|
| Book meeting (business email) | Yes (stage: booked) | - |
| Book meeting (personal email) | No | - |
| Reschedule meeting | No | No change |
| Cancel meeting | No | status → cancelled |
| Meeting ends | No | stage → met |
| Second booking, same company | No (uses existing) | No change |
