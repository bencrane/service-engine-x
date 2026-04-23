# new-booking-orchestrator — SERX DB write directive

**Agent ID:** `agent_011CaKVUQQ1uBt14rAZAfdAe`
**Triggered by:** Cal.com `BOOKING_CREATED` webhook. serx-webhooks ingests the raw payload into `webhook_events_raw` and POSTs an `event_ref` to managed-agents-x-api `/sessions/from-event`, which spawns this session.
**Scope of this doc:** What the agent must write to the SERX database. Other responsibilities (email sends, notifications, etc.) are out of scope here.

---

## Input contract

The managed-agents session initial message carries:

- `source` — always `"cal_com"`.
- `event_name` — always `"BOOKING_CREATED"` for this agent.
- `event_ref` — `{ "store": "serx_webhook_events_raw", "id": "<uuid>" }`. The UUID is the `webhook_events_raw.id` row that contains the full Cal.com payload.

Note what is **not** in the input: no pre-resolved `org_id`. Previously Pipedream did that resolution upstream; the new serx-webhooks → managed-agents pipeline is dumb and hands over only the event pointer. The agent resolves the org itself in step 2.

---

## Required writes (in order)

### 1. Fetch the raw payload

Call `serx_get_webhook_event({ event_id: event_ref.id })`. The response row has:

- `source` — `"cal_com"`
- `trigger_event` — `"BOOKING_CREATED"` (already extracted from the envelope at ingest time)
- `payload` — the full parsed JSON body from Cal.com. For `BOOKING_CREATED` the booking data lives under `payload.payload` (Cal.com's nested envelope is unchanged).

Extract from `payload.payload`:

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
| `payload.responses` (booking form answers) | see step 4/5 below |

### 2. Resolve org_id

Call `serx_resolve_org_from_event_type({ event_type_id: cal_event_type_id })`. The response includes the SERX `org_id` for the team that owns this Cal.com event type.

If resolution fails (404 or ambiguous team) → log an error and stop. Do not create a booking_event or meeting without an org.

### 3. Create the normalized booking event (audit row)

Call `serx_create_booking_event` with:

```json
{
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

Do **not** include `raw_event_id` — that field points at the legacy `cal_raw_events` table, not `webhook_events_raw`. Omit it.

This is an append-only audit trail. Duplicates are allowed by design.

### 4. Create the meeting (idempotent)

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

**What goes in `custom_fields`:** every key in `payload.responses` **except** the ones mapped to structured columns in step 5. Preserve the original keys. If unsure whether something is structured, include it — duplication in jsonb is cheap.

This tool is idempotent on `(org_id, cal_event_uid)` — safe to retry. It also creates or updates the linked `account` (by email domain) and minimal `contact` rows for each attendee. The response returns `meeting_id` and the resolved `contact_id` / `account_id`.

### 5. Enrich the primary contact with booking-form identity fields

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

---

## No "mark processed" step

Unlike the legacy Pipedream pipeline, this flow has no `serx_mark_cal_raw_event_processed` call. Dispatch state is tracked by serx-webhooks itself on `webhook_events_raw.dispatch_status` (set to `'dispatched'` when this session was spawned). The agent does not need to write back to `webhook_events_raw`.

---

## Error handling rules

- If `serx_get_webhook_event` returns 404 → the row doesn't exist (should not happen — serx-webhooks wrote it before dispatching). Log and stop.
- If `serx_resolve_org_from_event_type` returns 404 → log error and stop. No meeting is created without an org.
- If `serx_create_meeting_from_cal_event` returns with `created: false` → the meeting already existed (replay). Skip step 5. This is a successful no-op outcome.
- If `serx_upsert_contact` fails → log a warning, **continue**. The meeting already exists; contact enrichment is best-effort.
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
