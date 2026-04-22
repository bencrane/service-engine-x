# rescheduled-booking-orchestrator — SERX DB write directive

**Agent ID:** `agent_011CZvtd69ztjNr4FdDsxbsx`
**Triggered by:** Cal.com `BOOKING_RESCHEDULED` webhook via the Pipedream dispatcher.
**Scope of this doc:** What the agent must write to the SERX database. Other responsibilities (email sends, notifications, etc.) are out of scope here.

---

## Cal.com's rescheduling model (read this first)

Cal.com does **not** mutate bookings in place when they reschedule. Instead it issues a **brand-new booking** — new `uid`, new numeric `id`, new `startTime`/`endTime` — and flags the old one. The webhook payload carries both identifiers:

| Field | Meaning |
|---|---|
| `uid` / `id` | The **NEW** booking's identifiers |
| `rescheduledFromUid` | The **OLD** booking's uid (this is what SERX has stored already) |
| `rescheduledToUid` | Same as `uid` (redundant but present) |
| `reschedulingReason` | Optional free-text reason |
| `rescheduledByEmail` | Who triggered the reschedule |
| `startTime` / `endTime` | NEW meeting times |
| `attendees[]` | Carried over |

**Consequence:** if you look up the existing meeting by `payload.uid` you will find nothing, because SERX has it stored under the old uid. You must look up by `rescheduledFromUid`. `serx_create_meeting_from_cal_event` handles this correctly when passed `rescheduled_from_uid` — it flips the old meeting to `status='rescheduled'` and creates a new meeting row carrying forward `account_id` / `contact_id` / `deal_id`.

---

## Input contract

- `raw_event_id` — UUID of the stored raw payload.
- `org_id` — UUID of the SERX organization. Already resolved. **Do not re-resolve.**
- `trigger_event` — always `"BOOKING_RESCHEDULED"`.

---

## Required writes (in order)

### 1. Fetch the raw payload

Call `serx_get_cal_raw_event({ event_id: raw_event_id })`. Parse `payload.payload` (nested envelope). Extract at minimum:

- `uid` → new `cal_event_uid`
- `id` (or `bookingId`) → new `cal_booking_id`
- `rescheduledFromUid` → previous uid
- `startTime`, `endTime` → new times
- `title`, `attendees`, `organizer.email`
- `reschedulingReason`, `rescheduledByEmail` (both optional)

If `rescheduledFromUid` is missing from the payload, log a warning and proceed — `serx_create_meeting_from_cal_event` will simply create a fresh meeting row without linking back to a previous one.

### 2. Create the normalized booking event (audit row)

Call `serx_create_booking_event`:

```json
{
  "raw_event_id": "<raw_event_id>",
  "org_id": "<org_id>",
  "trigger_event": "BOOKING_RESCHEDULED",
  "cal_booking_uid": "<payload.uid>",
  "cal_booking_id": "<payload.id>",
  "title": "<payload.title>",
  "start_time": "<payload.startTime>",
  "end_time": "<payload.endTime>",
  "organizer_email": "<payload.organizer.email>"
}
```

Append-only — duplicates allowed by design.

### 3. Create the new meeting + flip old meeting to `rescheduled`

Call `serx_create_meeting_from_cal_event` with the **new** booking's identifiers AND the `rescheduled_from_uid` of the old one:

```json
{
  "org_id": "<org_id>",
  "cal_event_uid": "<payload.uid>",             // NEW uid
  "cal_booking_id": "<payload.id>",             // NEW id
  "rescheduled_from_uid": "<payload.rescheduledFromUid>",  // OLD uid
  "title": "<payload.title>",
  "start_time": "<payload.startTime>",          // NEW time
  "end_time": "<payload.endTime>",              // NEW time
  "organizer_email": "<payload.organizer.email>",
  "attendees": [{ "name": "<att.name>", "email": "<att.email>" }, ...],
  "status": "scheduled",
  "custom_fields": {
    "rescheduling_reason": "<payload.reschedulingReason, if present>",
    "rescheduled_by_email": "<payload.rescheduledByEmail, if present>",
    "rescheduled_from_uid": "<payload.rescheduledFromUid>"
  }
}
```

Inside this tool, the API will:
1. Look up the meeting with `cal_event_uid = rescheduledFromUid`.
2. If found: update that row to `status='rescheduled'`.
3. Insert a NEW meeting row for the new booking, carrying forward `account_id`, `contact_id`, and `deal_id` from the old meeting.

Omit `custom_fields` entries whose source values are absent. Never put `null` inside a key you populated — just skip the key.

### 4. Mark the raw event processed

Call `serx_mark_cal_raw_event_processed({ event_id: raw_event_id })`.

---

## What NOT to do

- Do **not** call `serx_update_meeting` on the old meeting yourself. `serx_create_meeting_from_cal_event` already flips its status when passed `rescheduled_from_uid`.
- Do **not** upsert contacts again — they were created on the original BOOKING_CREATED event. Attendee identity does not change on a reschedule.
- Do **not** create a new deal. If a deal was linked to the old meeting, the carry-forward above preserves that link on the new meeting.
- Do **not** re-resolve `org_id`.

---

## Error handling rules

- If `serx_get_cal_raw_event` returns 404 → log and stop; do not mark processed.
- If the payload's `rescheduledFromUid` is missing or points at a uid SERX doesn't have → the tool returns `created: true` with no old_meeting link and a warning like `rescheduled_from_uid did not match any existing meeting`. Continue; mark processed.
- If the new booking uid was already stored (replay) → `created: false` returned. Still call mark-processed. Successful no-op.
- If mark-processed fails → log and retry once.

---

## Return shape

```json
{
  "ok": true,
  "meeting_id": "<new meeting uuid>",
  "old_meeting_id": "<uuid or null>",
  "created": true,
  "warnings": []
}
```
