# cancelled-booking-orchestrator — SERX DB write directive

**Agent ID:** `agent_011CZvrV7PxgxUBi49DfwZzF`
**Triggered by:** Cal.com `BOOKING_CANCELLED` webhook. serx-webhooks ingests the raw payload into `webhook_events_raw` and POSTs an `event_ref` to managed-agents-x-api `/sessions/from-event`, which spawns this session.
**Scope of this doc:** What the agent must write to the SERX database. Other responsibilities (email sends, notifications, etc.) are out of scope here.

---

## Input contract

The managed-agents session initial message carries:

- `source` — always `"cal_com"`.
- `event_name` — always `"BOOKING_CANCELLED"`.
- `event_ref` — `{ "store": "serx_webhook_events_raw", "id": "<uuid>" }`.

No pre-resolved `org_id`. The agent resolves it itself.

---

## Required writes (in order)

### 1. Fetch the raw payload

Call `serx_get_webhook_event({ event_id: event_ref.id })`. Parse `payload.payload` (Cal.com's nested envelope). Extract:

- `uid` → `cal_event_uid` (this is the same uid as the original BOOKING_CREATED)
- `id` (or `bookingId`) → `cal_booking_id`
- `eventTypeId` → for org resolution
- `title`
- `startTime`, `endTime`
- `organizer.email`
- `cancellationReason` (optional free-text)
- `cancelledByEmail` (optional)

Unlike reschedule, cancellation does **not** issue a new uid — it's the same booking.

### 2. Resolve org_id

Call `serx_resolve_org_from_event_type({ event_type_id })`. If it fails → log and stop.

### 3. Create the normalized booking event (audit row)

Call `serx_create_booking_event`:

```json
{
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

Omit `raw_event_id` (legacy cal_raw_events column). Append-only — duplicates allowed by design.

### 4. Look up the existing meeting

Call `serx_get_meeting_by_cal_uid({ org_id, cal_event_uid: payload.uid })`. If that returns 404 (e.g. BOOKING_CREATED was missed), fall back to `serx_get_meeting_by_cal_booking_id({ org_id, cal_booking_id: payload.id })`.

If still not found: log a warning, skip step 5. **Do not create a meeting on cancellation.**

### 5. Update the meeting to `cancelled`

Call `serx_update_meeting`:

```json
{
  "org_id": "<org_id>",
  "meeting_id": "<meeting_id from step 4>",
  "status": "cancelled",
  "cancellation_reason": "<payload.cancellationReason, if present; otherwise omit this key>"
}
```

Omit `cancellation_reason` entirely when the payload has none — do not send `null`, do not send an empty string. The column is nullable and absence is valid.

---

## What NOT to do

- Do **not** insert a new meeting row.
- Do **not** touch contacts, accounts, or attendees — cancellation is purely a state change on the existing meeting.
- Do **not** touch deals. If the deal should close on cancellation, that's a separate business rule handled outside this orchestrator.
- Do **not** write back to `webhook_events_raw`. Dispatch state is tracked by serx-webhooks.

---

## Error handling rules

- If `serx_get_webhook_event` returns 404 → log and stop.
- If `serx_resolve_org_from_event_type` returns 404 → log and stop.
- If no meeting found by either uid or booking_id → log a warning like `cancellation received for unknown booking <uid>`, skip the meeting update. This can legitimately happen if BOOKING_CREATED was dropped upstream.
- If `serx_update_meeting` fails → log and let the managed-agents runtime retry the session.

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
