# new-booking-orchestrator — SERX DB write directive

**Agent ID:** `agent_011CaKVUQQ1uBt14rAZAfdAe`
**Triggered by:** Cal.com `BOOKING_CREATED` webhook via the Pipedream dispatcher.
**Scope of this doc:** What the agent must write to the SERX database. Other responsibilities (email sends, notifications, etc.) are out of scope here.

---

## Input contract

The Pipedream dispatcher invokes this agent with:

- `raw_event_id` — UUID of the row in `cal_raw_events` (or future `webhook_events_raw`) containing the full Cal.com payload.
- `org_id` — UUID of the SERX organization the booking belongs to. Already resolved upstream from `cal_team_id`. **Do not re-resolve.**
- `trigger_event` — always `"BOOKING_CREATED"` for this agent.

---

## Required writes (in order)

### 1. Fetch the raw payload

Call `serx_get_cal_raw_event({ event_id: raw_event_id })`. Parse `payload` (JSONB). For `BOOKING_CREATED` the booking data lives under `payload.payload` (nested envelope).

Extract:

| Source | Destination variable |
|---|---|
| `payload.uid` | `cal_event_uid` |
| `payload.bookingId` or `payload.id` | `cal_booking_id` |
| `payload.eventTypeId` | `cal_event_type_id` |
| `payload.title` | `title` |
| `payload.startTime` | `start_time` |
| `payload.endTime` | `end_time` |
| `payload.organizer.email` | `organizer_email` |
| `payload.attendees[]` | attendees (name, email) |
| `payload.responses` (booking form answers) | see step 3/4 below |

### 2. Create the normalized booking event (audit row)

Call `serx_create_booking_event` with:

```json
{
  "raw_event_id": "<raw_event_id>",
  "org_id": "<org_id>",
  "trigger_event": "BOOKING_CREATED",
  "cal_booking_uid": "<payload.uid>",
  "cal_booking_id": "<payload.bookingId>",
  "cal_event_type_id": "<payload.eventTypeId>",
  "title": "<payload.title>",
  "start_time": "<payload.startTime>",
  "end_time": "<payload.endTime>",
  "organizer_email": "<payload.organizer.email>",
  "organizer_name": "<payload.organizer.name>",
  "guests": ["<payload.additionalNotes guest emails if any>"]
}
```

This is an append-only audit trail. Duplicates are allowed by design.

### 3. Create the meeting (idempotent)

Call `serx_create_meeting_from_cal_event` with:

```json
{
  "org_id": "<org_id>",
  "cal_event_uid": "<payload.uid>",
  "cal_booking_id": "<payload.bookingId>",
  "title": "<payload.title>",
  "start_time": "<payload.startTime>",
  "end_time": "<payload.endTime>",
  "organizer_email": "<payload.organizer.email>",
  "attendees": [{ "name": "<att.name>", "email": "<att.email>" }, ...],
  "status": "scheduled",
  "notes": "<payload.responses.notes or payload.additionalNotes>",
  "custom_fields": {
    "<every booking-form field not mapped to a structured column below>": "<its value>"
  }
}
```

**What goes in `custom_fields`:** every key in `payload.responses` **except** the ones mapped to structured columns in step 4. Preserve the original keys. If unsure whether something is structured, include it — duplication in jsonb is cheap.

This tool is idempotent on `(org_id, cal_event_uid)` — safe to retry. It also creates or updates the linked `account` (by email domain) and minimal `contact` rows for each attendee. The response returns `meeting_id` and the resolved `contact_id` / `account_id`.

### 4. Enrich the primary contact with booking-form identity fields

The meeting-creation step above only sets `name_f` / `name_l` / `email` on contacts. The booking form may additionally collect phone, title, or company context. Enrich by calling `serx_upsert_contact` for the **primary attendee** (first attendee, typically the person who booked):

```json
{
  "org_id": "<org_id>",
  "email": "<primary attendee email>",
  "name_f": "<from name split>",
  "name_l": "<from name split>",
  "phone": "<payload.responses.phone or payload.responses['Phone number']>",
  "title": "<payload.responses.title if present>"
}
```

Field-name variations in `payload.responses` are common (`phone` vs `Phone number` vs `phoneNumber`). Try the obvious variants; if none present, omit the field from the upsert body. **Do not fail the orchestration if any individual form field is missing.**

### 5. Mark the raw event processed

Call `serx_mark_cal_raw_event_processed({ event_id: raw_event_id })`. This flips `processed_at` and prevents re-orchestration on retry.

---

## Error handling rules

- If `serx_get_cal_raw_event` returns 404 → the raw event doesn't exist. Log and stop; do not mark processed.
- If `serx_create_meeting_from_cal_event` returns with `created: false` → the meeting already existed (replay). Skip steps 4 and still call mark-processed. This is a successful no-op outcome.
- If `serx_upsert_contact` fails → log a warning, **continue**. The meeting already exists; contact enrichment is best-effort.
- If `serx_mark_cal_raw_event_processed` fails → log and retry once. Do not fail the orchestration for this alone.
- Never create a deal on `BOOKING_CREATED`. Deals are created separately when a meeting qualifies.

---

## Return shape

```json
{
  "ok": true,
  "meeting_id": "<uuid>",
  "contact_id": "<uuid of primary attendee>",
  "account_id": "<uuid or null>",
  "created": true,
  "warnings": []
}
```

If the booking already existed (replay), `created: false` and `meeting_id` points at the existing row.
