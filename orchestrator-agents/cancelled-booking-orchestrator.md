# cancelled-booking-orchestrator — SERX DB write directive

**Agent ID:** `agent_011CZvrV7PxgxUBi49DfwZzF`
**Triggered by:** Cal.com `BOOKING_CANCELLED` webhook via the Pipedream dispatcher.
**Scope of this doc:** What the agent must write to the SERX database. Other responsibilities (email sends, notifications, etc.) are out of scope here.

---

## Input contract

- `raw_event_id` — UUID of the stored raw payload.
- `org_id` — UUID of the SERX organization. Already resolved. **Do not re-resolve.**
- `trigger_event` — always `"BOOKING_CANCELLED"`.

---

## Required writes (in order)

### 1. Fetch the raw payload

Call `serx_get_cal_raw_event({ event_id: raw_event_id })`. Parse `payload.payload` (nested envelope). Extract:

- `uid` → `cal_event_uid` (this is the same uid as the original BOOKING_CREATED)
- `id` (or `bookingId`) → `cal_booking_id`
- `title`
- `startTime`, `endTime`
- `organizer.email`
- `cancellationReason` (optional free-text)
- `cancelledByEmail` (optional)

Unlike reschedule, cancellation does **not** issue a new uid — it's the same booking.

### 2. Create the normalized booking event (audit row)

Call `serx_create_booking_event`:

```json
{
  "raw_event_id": "<raw_event_id>",
  "org_id": "<org_id>",
  "trigger_event": "BOOKING_CANCELLED",
  "cal_booking_uid": "<payload.uid>",
  "cal_booking_id": "<payload.id>",
  "title": "<payload.title>",
  "start_time": "<payload.startTime>",
  "end_time": "<payload.endTime>",
  "organizer_email": "<payload.organizer.email>"
}
```

Append-only — duplicates allowed by design.

### 3. Look up the existing meeting

Call `serx_get_meeting_by_cal_uid({ org_id, cal_event_uid: payload.uid })`. If that returns 404 (e.g. BOOKING_CREATED was missed), fall back to `serx_get_meeting_by_cal_booking_id({ org_id, cal_booking_id: payload.id })`.

If still not found: log a warning, skip step 4, continue to step 5. **Do not create a meeting on cancellation.**

### 4. Update the meeting to `cancelled`

Call `serx_update_meeting`:

```json
{
  "org_id": "<org_id>",
  "meeting_id": "<meeting_id from step 3>",
  "status": "cancelled",
  "cancellation_reason": "<payload.cancellationReason, if present; otherwise omit this key>"
}
```

Omit `cancellation_reason` entirely when the payload has none — do not send `null`, do not send an empty string. The column is nullable and absence is valid.

### 5. Mark the raw event processed

Call `serx_mark_cal_raw_event_processed({ event_id: raw_event_id })`.

---

## What NOT to do

- Do **not** insert a new meeting row.
- Do **not** touch contacts, accounts, or attendees — cancellation is purely a state change on the existing meeting.
- Do **not** touch deals. If the deal should close on cancellation, that's a separate business rule handled outside this orchestrator.
- Do **not** re-resolve `org_id`.

---

## Error handling rules

- If `serx_get_cal_raw_event` returns 404 → log and stop; do not mark processed.
- If no meeting found by either uid or booking_id → log a warning like `cancellation received for unknown booking <uid>`, skip the meeting update, still call mark-processed. This can legitimately happen if BOOKING_CREATED was dropped upstream.
- If `serx_update_meeting` fails → log and retry once. If still failing, do not mark processed so the event can be replayed.
- If mark-processed fails → log and retry once.

---

## Return shape

```json
{
  "ok": true,
  "meeting_id": "<uuid or null>",
  "status_set": "cancelled",
  "cancellation_reason_recorded": true,
  "warnings": []
}
```

`meeting_id` is null and `warnings` is populated when no existing meeting was found.
