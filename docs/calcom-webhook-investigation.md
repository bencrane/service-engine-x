# Cal.com Webhook Handling Investigation

## 1. Webhook receiver routes

### Primary Cal.com Webhook Receiver
**File:** `/Users/benjamincrane/service-engine-x/service-engine-x-api/app/routers/cal_webhooks.py`

**Route handler:**
```python
@router.post("/api/webhooks/cal")
async def cal_webhook(request: Request) -> JSONResponse:
    """Receive Cal.com webhook, verify HMAC, store, and route."""
    raw_body = await request.body()

    # --- HMAC verification ---
    signature = request.headers.get("X-Cal-Signature-256")
    if not _verify_signature(raw_body, signature):
        return JSONResponse(status_code=401, content={"error": "invalid signature"})

    # --- Parse ---
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "invalid JSON"})

    fields = _extract_fields(payload)

    # --- Store in cal_raw_events ---
    supabase = get_supabase()
    row = {
        "trigger_event": fields["trigger_event"],
        "payload": payload,
        "cal_event_uid": fields["cal_event_uid"],
        "organizer_email": fields["organizer_email"],
        "attendee_emails": fields["attendee_emails"],
        "event_type_id": fields["event_type_id"],
        "processed": False,
    }
    result = supabase.table("cal_raw_events").insert(row).execute()
    event_row = result.data[0] if result.data else row

    logger.info(
        "cal_webhook stored event=%s uid=%s id=%s",
        fields["trigger_event"],
        fields["cal_event_uid"],
        event_row.get("id"),
    )

    # --- Route to handler ---
    route_cal_event(event_row)

    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "trigger_event": fields["trigger_event"],
            "event_id": event_row.get("id"),
        },
    )
```

**HTTP method:** `POST`
**Path:** `/api/webhooks/cal`
**Prefix/Tags:** `tags=["Cal.com Webhooks"]` (no router prefix)
**Registration:** Included in main.py via `app.include_router(cal_webhooks_router)` at line 164

### Legacy Cal.com Webhook Sink
**File:** `/Users/benjamincrane/service-engine-x/service-engine-x-api/app/routers/calcom_webhooks.py`

**Route handler:**
```python
@router.post("")
async def calcom_webhook_sink(request: Request) -> JSONResponse:
    """Catch any Cal.com webhook event and store the raw payload."""
    body = await request.body()
    payload = json.loads(body)

    event_type = payload.get("triggerEvent", payload.get("type", "unknown"))

    supabase = get_supabase()
    supabase.table("cal_webhook_events_raw").insert(
        {
            "trigger_event": event_type,
            "payload": payload,
            "cal_booking_uid": _extract_booking_uid(payload),
        }
    ).execute()

    return JSONResponse(
        status_code=200,
        content={"status": "captured", "event_type": event_type},
    )
```

**HTTP method:** `POST`
**Path:** `/api/webhooks/calcom`
**Prefix:** `/api/webhooks/calcom`
**Tags:** `["Cal.com Webhooks"]`
**Registration:** Included in main.py via `app.include_router(calcom_webhooks_router)` at line 165
**Status:** LEGACY/DEPRECATED — maintains immutable audit log in `cal_webhook_events_raw` table (original sink). Primary webhook handler is `cal_webhooks.py`.

---

## 2. Signature verification

### Verification Logic
**File:** `/Users/benjamincrane/service-engine-x/service-engine-x-api/app/routers/cal_webhooks.py`

**Verbatim verification code:**
```python
def _verify_signature(raw_body: bytes, signature_header: str | None) -> bool:
    """Verify X-Cal-Signature-256 HMAC-SHA256 signature.

    If CALCOM_WEBHOOK_SECRET is empty (local dev), verification is skipped.
    """
    secret = settings.CAL_WEBHOOK_SECRET
    if not secret:
        logger.warning("CAL_WEBHOOK_SECRET not set — skipping HMAC verification")
        return True

    if not signature_header:
        logger.warning("Missing X-Cal-Signature-256 header")
        return False

    expected = hmac.new(
        secret.encode(), raw_body, hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature_header)
```

**Header name:** `X-Cal-Signature-256`
**Algorithm:** HMAC-SHA256
**Secret env var:** `CAL_WEBHOOK_SECRET` (from `app.config.Settings`)
**Body used:** Raw request body (as bytes, not parsed JSON)
**Verification behavior:** 
- Returns `True` (skips verification) if `CAL_WEBHOOK_SECRET` is empty (local dev)
- Returns `False` if header is missing when secret is set
- Uses `hmac.compare_digest()` for constant-time comparison
- Computes digest as `.hexdigest()` (hex string format)

---

## 3. Payload parsing

### Dual Payload Shape Handling
**File:** `/Users/benjamincrane/service-engine-x/service-engine-x-api/app/routers/cal_webhooks.py`

**Constant defining flat payload triggers:**
```python
FLAT_PAYLOAD_TRIGGERS = {"MEETING_STARTED", "MEETING_ENDED"}
```

**Field extraction logic:**
```python
def _extract_fields(payload: dict[str, Any]) -> dict[str, Any]:
    """Extract storage fields from either payload shape.

    Standard envelope:  { triggerEvent, createdAt, payload: { uid, hosts, attendees, eventTypeId, ... } }
    Flat (meetings):    { triggerEvent, createdAt, bookingId, roomName, ... }
    """
    trigger_event = payload.get("triggerEvent", "unknown")
    is_flat = trigger_event in FLAT_PAYLOAD_TRIGGERS

    if is_flat:
        # Flat shape — fields are top-level. No uid/hosts/attendees/eventTypeId.
        return {
            "trigger_event": trigger_event,
            "cal_event_uid": None,
            "organizer_email": None,
            "attendee_emails": [],
            "event_type_id": None,
        }

    # Standard envelope — booking data lives under payload.
    inner = payload.get("payload", {})
    if not isinstance(inner, dict):
        inner = {}

    # organizer_email: first host's email
    hosts = inner.get("hosts") or []
    organizer_email = hosts[0].get("email") if hosts else None

    # attendee_emails: all attendee emails + guests
    attendees = inner.get("attendees") or []
    attendee_emails = [a.get("email") for a in attendees if a.get("email")]
    guests = inner.get("guests") or []
    attendee_emails.extend(g for g in guests if isinstance(g, str))

    return {
        "trigger_event": trigger_event,
        "cal_event_uid": inner.get("uid"),
        "organizer_email": organizer_email,
        "attendee_emails": attendee_emails,
        "event_type_id": inner.get("eventTypeId"),
    }
```

### Normalization Models
**File:** `/Users/benjamincrane/service-engine-x/service-engine-x-api/app/routers/internal_cal_events.py`

**Pydantic models for API requests:**
```python
class RawEventCreateRequest(BaseModel):
    trigger_event: str
    payload: dict[str, Any]
    cal_event_uid: str | None = None
    organizer_email: str | None = None
    attendee_emails: list[str] = Field(default_factory=list)
    event_type_id: int | None = None


class BookingEventCreateRequest(BaseModel):
    raw_event_id: UUID | None = None
    org_id: UUID | None = None
    trigger_event: str | None = None
    cal_booking_uid: str | None = None
    cal_booking_id: int | None = None
    cal_event_type_id: int | None = None
    title: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: str | None = None
    location: str | None = None
    meeting_url: str | None = None
    organizer_email: str | None = None
    organizer_name: str | None = None
    organizer_cal_user_id: int | None = None
    guests: list[str] = Field(default_factory=list)
    event_occurred_at: datetime | None = None
    raw_payload: dict[str, Any] | None = None


class BookingAttendeeItem(BaseModel):
    booking_event_id: UUID | None = None
    org_id: UUID | None = None
    cal_booking_uid: str | None = None
    cal_booking_id: int | None = None
    role: str = "attendee"
    name: str | None = None
    email: str
    timezone: str | None = None
    language: str | None = None
    phone_number: str | None = None
    absent: bool | None = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"attendee", "host"}:
            raise ValueError("role must be attendee or host")
        return normalized


class RecordingCreateRequest(BaseModel):
    raw_event_id: UUID | None = None
    org_id: UUID | None = None
    cal_booking_uid: str | None = None
    cal_booking_id: int | None = None
    cal_recording_id: str | None = None
    room_name: str | None = None
    start_ts: datetime | None = None
    status: str | None = None
    duration_seconds: int | None = None
    share_token: str | None = None
    max_participants: int | None = None
    download_link: str | None = None
    transcript_url: str | None = None
    raw_payload: dict[str, Any] | None = None
```

### Payload Normalization Functions
**Booking event normalization:**
```python
def _normalize_booking_event_from_payload(raw_payload: dict[str, Any]) -> dict[str, Any]:
    payload_obj = _extract_payload_obj(raw_payload)
    organizer_obj = payload_obj.get("organizer")
    organizer = organizer_obj if isinstance(organizer_obj, dict) else {}
    guests = _as_list_strings(payload_obj.get("guests"))
    trigger_event = _extract_trigger_event(raw_payload)

    return {
        "trigger_event": trigger_event,
        "cal_booking_uid": _extract_booking_uid(raw_payload),
        "cal_booking_id": _extract_booking_id(raw_payload),
        "cal_event_type_id": payload_obj.get("eventTypeId") or payload_obj.get("eventType"),
        "title": payload_obj.get("title") or raw_payload.get("title"),
        "start_time": _parse_dt(payload_obj.get("startTime") or payload_obj.get("start")),
        "end_time": _parse_dt(payload_obj.get("endTime") or payload_obj.get("end")),
        "status": payload_obj.get("status") or raw_payload.get("status"),
        "location": _extract_location(payload_obj.get("location")),
        "meeting_url": _extract_meeting_url(payload_obj, raw_payload),
        "organizer_email": organizer.get("email") or raw_payload.get("organizerEmail"),
        "organizer_name": organizer.get("name") or raw_payload.get("organizerName"),
        "organizer_cal_user_id": organizer.get("id") or payload_obj.get("userId"),
        "guests": guests,
        "event_occurred_at": _parse_dt(
            raw_payload.get("createdAt") or payload_obj.get("createdAt")
        ),
    }
```

**Attendees normalization:**
```python
def _normalize_attendees_from_payload(raw_payload: dict[str, Any]) -> list[dict[str, Any]]:
    payload_obj = _extract_payload_obj(raw_payload)
    booking_uid = _extract_booking_uid(raw_payload)
    booking_id = _extract_booking_id(raw_payload)

    attendees: list[dict[str, Any]] = []
    payload_attendees = payload_obj.get("attendees")
    if isinstance(payload_attendees, list):
        for attendee in payload_attendees:
            if not isinstance(attendee, dict):
                continue
            email = attendee.get("email")
            if not isinstance(email, str) or not email.strip():
                continue
            attendees.append(
                {
                    "cal_booking_uid": booking_uid,
                    "cal_booking_id": booking_id,
                    "role": "attendee",
                    "name": attendee.get("name"),
                    "email": email.strip().lower(),
                    "timezone": attendee.get("timeZone") or attendee.get("timezone"),
                    "language": attendee.get("language"),
                    "phone_number": attendee.get("phoneNumber") or attendee.get("phone"),
                    "absent": attendee.get("absent"),
                }
            )

    payload_hosts = payload_obj.get("hosts")
    if isinstance(payload_hosts, list):
        for host in payload_hosts:
            if not isinstance(host, dict):
                continue
            email = host.get("email")
            if not isinstance(email, str) or not email.strip():
                continue
            attendees.append(
                {
                    "cal_booking_uid": booking_uid,
                    "cal_booking_id": booking_id,
                    "role": "host",
                    "name": host.get("name"),
                    "email": email.strip().lower(),
                    "timezone": host.get("timeZone") or host.get("timezone"),
                    "language": host.get("language"),
                    "phone_number": host.get("phoneNumber") or host.get("phone"),
                    "absent": host.get("absent"),
                }
            )
    return attendees
```

### Payload Variation Handling
- **Standard envelope shape:** Has `triggerEvent` and nested `payload: { uid, hosts, attendees, eventTypeId, ... }`
- **Flat shape (MEETING_STARTED/MEETING_ENDED):** Fields at top-level (bookingId, roomName, etc.), no nested payload
- **Booking UID extraction:** Tries `payload.uid` first (nested), then falls back to top-level `uid`
- **Booking ID extraction:** Tries multiple field names: `bookingId`, `booking_id`, `id` (both top-level and nested)
- **DateTime parsing:** Converts ISO 8601 strings with or without 'Z' suffix to ISO format
- **Email normalization:** Strips whitespace and converts to lowercase

---

## 4. Storage

### Table Definitions

#### `cal_raw_events` — Agent-routable webhook event log
**File:** `/Users/benjamincrane/service-engine-x/service-engine-x-api/migrations/016_cal_raw_events.sql`

**DDL:**
```sql
CREATE TABLE IF NOT EXISTS cal_raw_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trigger_event   TEXT NOT NULL,
    payload         JSONB NOT NULL,
    cal_event_uid   TEXT,
    organizer_email TEXT,
    attendee_emails JSONB NOT NULL DEFAULT '[]'::jsonb,
    event_type_id   BIGINT,
    processed       BOOLEAN NOT NULL DEFAULT FALSE,
    processed_by    TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cal_raw_events_trigger_event ON cal_raw_events (trigger_event);
CREATE INDEX idx_cal_raw_events_cal_event_uid ON cal_raw_events (cal_event_uid);
CREATE INDEX idx_cal_raw_events_processed     ON cal_raw_events (processed);
CREATE INDEX idx_cal_raw_events_created_at    ON cal_raw_events (created_at DESC);
```

**Stored:** Raw JSON payload + extracted fields (trigger_event, cal_event_uid, organizer_email, attendee_emails, event_type_id)
**Processing state:** `processed` (boolean), `processed_by` (text label for agent type)
**Purpose:** Agent-routable event log; used by `cal_webhooks.py` to store and dispatch to handlers

---

#### `cal_webhook_events_raw` — Immutable audit log
**File:** `/Users/benjamincrane/service-engine-x/service-engine-x-api/migrations/014_replace_calcom_webhook_log_with_cal_normalization_tables.sql`

**DDL:**
```sql
CREATE TABLE cal_webhook_events_raw (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trigger_event TEXT NOT NULL,
    payload JSONB NOT NULL,
    org_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    cal_booking_uid TEXT,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

CREATE INDEX idx_cal_webhook_events_raw_unprocessed
    ON cal_webhook_events_raw (received_at)
    WHERE processed_at IS NULL;
CREATE INDEX idx_cal_webhook_events_raw_booking_uid
    ON cal_webhook_events_raw (cal_booking_uid);
CREATE INDEX idx_cal_webhook_events_raw_trigger_event_received_at
    ON cal_webhook_events_raw (trigger_event, received_at DESC);
CREATE INDEX idx_cal_webhook_events_raw_org_id_received_at
    ON cal_webhook_events_raw (org_id, received_at DESC);

CREATE OR REPLACE FUNCTION enforce_cal_webhook_events_raw_immutability()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.trigger_event IS DISTINCT FROM OLD.trigger_event
       OR NEW.payload IS DISTINCT FROM OLD.payload
       OR NEW.org_id IS DISTINCT FROM OLD.org_id
       OR NEW.cal_booking_uid IS DISTINCT FROM OLD.cal_booking_uid
       OR NEW.received_at IS DISTINCT FROM OLD.received_at THEN
        RAISE EXCEPTION 'cal_webhook_events_raw is immutable; only processed_at can be updated';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_cal_webhook_events_raw_immutable ON cal_webhook_events_raw;
CREATE TRIGGER trg_cal_webhook_events_raw_immutable
BEFORE UPDATE ON cal_webhook_events_raw
FOR EACH ROW
EXECUTE FUNCTION enforce_cal_webhook_events_raw_immutability();
```

**Stored:** Raw JSON payload + org_id, trigger_event, cal_booking_uid, received_at, processed_at
**Immutability:** Enforced via trigger; only `processed_at` can be updated
**Purpose:** Legacy immutable audit log used by `calcom_webhooks.py` (deprecated sink)

---

#### `cal_booking_events` — Normalized booking lifecycle events
**File:** `/Users/benjamincrane/service-engine-x/service-engine-x-api/migrations/014_replace_calcom_webhook_log_with_cal_normalization_tables.sql`

**DDL:**
```sql
CREATE TABLE cal_booking_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_event_id UUID REFERENCES cal_webhook_events_raw(id) ON DELETE SET NULL,
    org_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    trigger_event TEXT NOT NULL,
    cal_booking_uid TEXT,
    cal_booking_id BIGINT,
    cal_event_type_id BIGINT,
    title TEXT,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    status TEXT,
    location TEXT,
    meeting_url TEXT,
    organizer_email TEXT,
    organizer_name TEXT,
    organizer_cal_user_id BIGINT,
    guests JSONB NOT NULL DEFAULT '[]'::jsonb,
    event_occurred_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cal_booking_events_booking_uid_created
    ON cal_booking_events (cal_booking_uid, created_at DESC);
CREATE INDEX idx_cal_booking_events_booking_id_created
    ON cal_booking_events (cal_booking_id, created_at DESC);
CREATE INDEX idx_cal_booking_events_trigger_event_created
    ON cal_booking_events (trigger_event, created_at DESC);
CREATE INDEX idx_cal_booking_events_org_id_created
    ON cal_booking_events (org_id, created_at DESC);
CREATE INDEX idx_cal_booking_events_raw_event_id
    ON cal_booking_events (raw_event_id);
```

**Stored:** Extracted fields (trigger_event, cal_booking_uid, cal_booking_id, cal_event_type_id, title, start_time, end_time, status, location, meeting_url, organizer_email, organizer_name, organizer_cal_user_id, guests, event_occurred_at)
**Deduplication:** Duplicates allowed by design (comment: "for auditability/replay safety")
**Purpose:** Normalized booking lifecycle events; allows querying by booking uid/id

---

#### `cal_booking_attendees` — Attendees and hosts per booking
**File:** `/Users/benjamincrane/service-engine-x/service-engine-x-api/migrations/014_replace_calcom_webhook_log_with_cal_normalization_tables.sql`

**DDL:**
```sql
CREATE TABLE cal_booking_attendees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_event_id UUID REFERENCES cal_booking_events(id) ON DELETE CASCADE,
    org_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    cal_booking_uid TEXT,
    cal_booking_id BIGINT,
    role TEXT NOT NULL DEFAULT 'attendee',
    name TEXT,
    email TEXT NOT NULL,
    timezone TEXT,
    language TEXT,
    phone_number TEXT,
    absent BOOLEAN,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT cal_booking_attendees_role_check
        CHECK (role IN ('attendee', 'host'))
);

ALTER TABLE cal_booking_attendees
    ADD CONSTRAINT uq_cal_booking_attendees_uid_email_role
    UNIQUE (cal_booking_uid, email, role);
CREATE INDEX idx_cal_booking_attendees_booking_uid
    ON cal_booking_attendees (cal_booking_uid);
CREATE INDEX idx_cal_booking_attendees_booking_id
    ON cal_booking_attendees (cal_booking_id);
CREATE INDEX idx_cal_booking_attendees_booking_event_id
    ON cal_booking_attendees (booking_event_id);
CREATE INDEX idx_cal_booking_attendees_org_id
    ON cal_booking_attendees (org_id);
```

**Stored:** Extracted attendee/host data (role, name, email, timezone, language, phone_number, absent)
**Deduplication:** UNIQUE constraint on (cal_booking_uid, email, role); bulk operations use UPSERT on conflict
**Purpose:** Lookup attendees/hosts per booking; can have multiple rows per booking (one per person)

---

#### `cal_recordings` — Cal.com recording metadata
**File:** `/Users/benjamincrane/service-engine-x/service-engine-x-api/migrations/014_replace_calcom_webhook_log_with_cal_normalization_tables.sql`

**DDL:**
```sql
CREATE TABLE cal_recordings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_event_id UUID REFERENCES cal_webhook_events_raw(id) ON DELETE SET NULL,
    org_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    cal_booking_uid TEXT,
    cal_booking_id BIGINT,
    cal_recording_id TEXT NOT NULL UNIQUE,
    room_name TEXT,
    start_ts TIMESTAMPTZ,
    status TEXT,
    duration_seconds INTEGER,
    share_token TEXT,
    max_participants INTEGER,
    download_link TEXT,
    transcript_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cal_recordings_booking_uid_created
    ON cal_recordings (cal_booking_uid, created_at DESC);
CREATE INDEX idx_cal_recordings_booking_id_created
    ON cal_recordings (cal_booking_id, created_at DESC);
CREATE INDEX idx_cal_recordings_org_id_created
    ON cal_recordings (org_id, created_at DESC);
CREATE INDEX idx_cal_recordings_raw_event_id
    ON cal_recordings (raw_event_id);
```

**Stored:** Recording metadata from RECORDING_READY events (room_name, start_ts, status, duration_seconds, share_token, max_participants, download_link, transcript_url)
**Deduplication:** UNIQUE constraint on cal_recording_id; UPSERT on conflict during updates
**Purpose:** Track recording availability and metadata

---

#### `cal_event_type_cache` — Event type slug/title cache
**File:** `/Users/benjamincrane/service-engine-x/service-engine-x-api/migrations/013_add_meetings_deals_and_cal_event_type_cache.sql`

**DDL:**
```sql
CREATE TABLE cal_event_type_cache (
    event_type_id    BIGINT PRIMARY KEY,
    org_id           UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    cal_team_id      INTEGER NOT NULL,
    event_type_slug  TEXT,
    event_type_title TEXT,
    raw_response     JSONB NOT NULL DEFAULT '{}'::jsonb,
    refreshed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cal_event_type_cache_org_id ON cal_event_type_cache(org_id);
CREATE INDEX idx_cal_event_type_cache_team_id ON cal_event_type_cache(cal_team_id);
CREATE INDEX idx_cal_event_type_cache_refreshed_at ON cal_event_type_cache(refreshed_at DESC);
```

**Stored:** Cal.com eventTypeId to team/org resolution; slug and title for display
**Purpose:** Cache to avoid repeated API calls for event type metadata

---

#### `meetings` and `deals` — Linked to Cal.com events
**File:** `/Users/benjamincrane/service-engine-x/service-engine-x-api/migrations/013_add_meetings_deals_and_cal_event_type_cache.sql`

**meetings table:**
```sql
CREATE TABLE meetings (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id              UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    account_id          UUID REFERENCES accounts(id) ON DELETE SET NULL,
    contact_id          UUID REFERENCES contacts(id) ON DELETE SET NULL,
    deal_id             UUID REFERENCES deals(id) ON DELETE SET NULL,
    cal_event_uid       VARCHAR(255),
    cal_booking_id      BIGINT,
    title               VARCHAR(255) NOT NULL,
    start_time          TIMESTAMPTZ NOT NULL,
    end_time            TIMESTAMPTZ NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    organizer_email     VARCHAR(255),
    attendee_emails     JSONB NOT NULL DEFAULT '[]'::jsonb,
    notes               TEXT,
    recording_url       TEXT,
    transcript_url      TEXT,
    host_no_show        BOOLEAN NOT NULL DEFAULT FALSE,
    guest_no_show       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT meetings_status_check
        CHECK (status IN ('pending', 'scheduled', 'in_progress', 'completed', 'cancelled', 'rejected', 'no_show', 'rescheduled'))
);

CREATE UNIQUE INDEX idx_meetings_cal_event_uid_unique
    ON meetings(cal_event_uid)
    WHERE cal_event_uid IS NOT NULL;

CREATE UNIQUE INDEX idx_meetings_cal_booking_id_unique
    ON meetings(cal_booking_id)
    WHERE cal_booking_id IS NOT NULL;
```

**deals table:**
```sql
CREATE TABLE deals (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id                  UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    account_id              UUID REFERENCES accounts(id) ON DELETE SET NULL,
    contact_id              UUID REFERENCES contacts(id) ON DELETE SET NULL,
    proposal_id             UUID REFERENCES proposals(id) ON DELETE SET NULL,
    title                   VARCHAR(255) NOT NULL,
    status                  VARCHAR(20) NOT NULL DEFAULT 'qualified',
    value                   DECIMAL(12,2),
    source                  VARCHAR(50),
    referred_by_account_id  UUID REFERENCES accounts(id) ON DELETE SET NULL,
    lost_reason             TEXT,
    notes                   TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at               TIMESTAMPTZ,
    deleted_at              TIMESTAMPTZ,
    CONSTRAINT deals_status_check
        CHECK (status IN ('qualified', 'proposal_sent', 'negotiating', 'won', 'lost'))
);
```

**Stored:** High-level meeting/deal records linked to Cal.com bookings via cal_event_uid/cal_booking_id

---

## 5. Processing flow

### Webhook receipt and storage
1. Cal.com sends HTTP POST to `/api/webhooks/cal` with `X-Cal-Signature-256` header
2. `cal_webhook()` handler in `cal_webhooks.py` receives request
3. Signature verified via HMAC-SHA256 against `CAL_WEBHOOK_SECRET`
4. Payload parsed as JSON; fields extracted via `_extract_fields()` (handles both envelope and flat shapes)
5. Row inserted into `cal_raw_events` table with:
   - Full raw `payload` (JSONB)
   - Extracted fields: `trigger_event`, `cal_event_uid`, `organizer_email`, `attendee_emails`, `event_type_id`
   - `processed: false`, `processed_by: null`
6. Returns 200 with event ID and trigger_event

### Routing to handlers
**File:** `/Users/benjamincrane/service-engine-x/service-engine-x-api/app/services/cal_event_handlers.py`

After storage, `route_cal_event(event_row)` is called:

```python
def route_cal_event(event_row: dict[str, Any]) -> None:
    """Dispatch an event row to the appropriate handler, or log as unhandled."""
    trigger = event_row.get("trigger_event", "unknown")
    event_id = event_row.get("id", "?")

    handler_entry = _ROUTED_EVENTS.get(trigger)
    if handler_entry is None:
        logger.info("unhandled trigger=%s id=%s — stored only", trigger, event_id)
        return

    handler_fn, agent_type = handler_entry
    handler_fn(event_row)
```

**Registered handlers (as of current code):**
- `BOOKING_CREATED` → `handle_booking_created()` (agent_type: `booking_created_agent`)
- `BOOKING_RESCHEDULED` → `handle_booking_rescheduled()` (agent_type: `booking_rescheduled_agent`)
- `BOOKING_CANCELLED` → `handle_booking_cancelled()` (agent_type: `booking_cancelled_agent`)
- `MEETING_ENDED` → `handle_meeting_ended()` (agent_type: `meeting_ended_agent`)

**Unhandled events:** Logged and stored only; no downstream dispatch

### Handler flow
Each registered handler currently calls:
```python
_mark_processed(event_id, agent_type)
```

Which updates the `cal_raw_events` row:
```python
def _mark_processed(event_id: str, agent_type: str) -> None:
    """Mark a cal_raw_events row as processed."""
    supabase = get_supabase()
    supabase.table("cal_raw_events").update(
        {"processed": True, "processed_by": agent_type}
    ).eq("id", event_id).execute()
```

### Downstream integration (from agent routing table)
**File:** `/Users/benjamincrane/service-engine-x/service-engine-x-api/migrations/017_cal_webhook_agent_routes.sql`

The `cal_webhook_agent_routes` table maps trigger events to Pipedream-managed agents:
```sql
CREATE TABLE cal_webhook_agent_routes (
    event_name       TEXT PRIMARY KEY,
    description      TEXT,
    agent_id         TEXT,
    environment_id   TEXT NOT NULL,
    credential_vault TEXT NOT NULL,
    enabled          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

Populated with agent IDs for:
- `BOOKING_CREATED` → `agent_011CZtixhAnM2rgE68RbSbTA`
- `BOOKING_RESCHEDULED` → `agent_011CZvtd69ztjNr4FdDsxbsx`
- `BOOKING_CANCELLED` → `agent_011CZvrV7PxgxUBi49DfwZzF`
- `BOOKING_REJECTED` → `agent_011CZvtgrR7qc1D845Tc8Rbo`
- Other events have `agent_id: NULL` (no handler yet)

### Task instruction templating
**File:** `/Users/benjamincrane/service-engine-x/service-engine-x-api/migrations/018_cal_webhook_agent_routes_task_template.sql`

Each route has an optional `task_instruction_template` column with placeholders (`{raw_event_id}`, `{org_id}`, `{trigger_event}`).

Example (BOOKING_CREATED):
```
Dispatch for BOOKING_CREATED.
raw_event_id: {raw_event_id}
org_id: {org_id}
trigger_event: BOOKING_CREATED
Execute the new-booking pipeline per your system prompt.
```

Pipedream renders this template into the user message dispatched to the managed agent.

### Deduplication and idempotency
- Webhook handler does not deduplicate incoming events; raw payload stored as-is
- `cal_booking_events` intentionally allows duplicates ("for auditability/replay safety") — comment at line 422 in internal_cal_events.py
- `cal_booking_attendees` uses UPSERT on `(cal_booking_uid, email, role)` constraint — allows re-processing attendee lists without duplicate rows

### No explicit replay protection
- No idempotency key / deduplication ID in stored events
- No timestamp-based duplicate detection
- Replay safety relies on downstream handlers checking duplicates (e.g., agent logic, UPSERT constraints on downstream tables)

---

## 6. Event types handled

**File:** `/Users/benjamincrane/service-engine-x/service-engine-x-api/app/services/cal_event_handlers.py` and `/Users/benjamincrane/service-engine-x/service-engine-x-api/app/routers/internal_cal_events.py`

### Supported event types (from BOOKING_EVENT_TYPES constant)
```python
BOOKING_EVENT_TYPES = {
    "BOOKING_CREATED",
    "BOOKING_REQUESTED",
    "BOOKING_RESCHEDULED",
    "BOOKING_CANCELLED",
    "BOOKING_REJECTED",
    "BOOKING_NO_SHOW_UPDATED",
    "BOOKING_PAYMENT_INITIATED",
    "BOOKING_PAID",
    "INSTANT_MEETING",
    "MEETING_STARTED",
    "MEETING_ENDED",
}
```

### Routed events (with handlers in _ROUTED_EVENTS)
1. **BOOKING_CREATED** — New booking created
   - Handler: `handle_booking_created()`
   - Agent: `booking_created_agent`
   - Action: Marks as processed, awaits agent dispatch

2. **BOOKING_RESCHEDULED** — Existing booking rescheduled to new time
   - Handler: `handle_booking_rescheduled()`
   - Agent: `booking_rescheduled_agent`
   - Action: Marks as processed, awaits agent dispatch

3. **BOOKING_CANCELLED** — Booking cancelled by host or attendee
   - Handler: `handle_booking_cancelled()`
   - Agent: `booking_cancelled_agent`
   - Action: Marks as processed, awaits agent dispatch

4. **MEETING_ENDED** — Cal Video meeting ended (flat payload)
   - Handler: `handle_meeting_ended()`
   - Agent: `meeting_ended_agent`
   - Action: Marks as processed, awaits agent dispatch

### Unrouted events (stored only, no handler)
These are stored in `cal_raw_events` and `cal_webhook_events_raw` but have no registered handler:
- `BOOKING_REQUESTED` — Pending booking (awaiting confirmation)
- `BOOKING_REJECTED` — Host rejected pending booking
- `BOOKING_NO_SHOW_UPDATED` — No-show status updated
- `BOOKING_PAYMENT_INITIATED` — Payment process started
- `BOOKING_PAID` — Payment completed
- `INSTANT_MEETING` — Instant meeting created (team event types)
- `MEETING_STARTED` — Cal Video meeting started
- `RECORDING_READY` — Recording ready for download
- `RECORDING_TRANSCRIPTION_GENERATED` — Transcription generated
- `AFTER_HOSTS_CAL_VIDEO_NO_SHOW` — Host didn't join Cal Video
- `AFTER_GUESTS_CAL_VIDEO_NO_SHOW` — Guest didn't join Cal Video
- `FORM_SUBMITTED` — Routing form submitted (event created)
- `FORM_SUBMITTED_NO_EVENT` — Routing form submitted (no event)
- `ROUTING_FORM_FALLBACK_HIT` — Routing form fallback hit
- `OOO_CREATED` — Out-of-office entry created
- `DELEGATION_CREDENTIAL_ERROR` — Delegation credential error

---

## 7. Environment variables

**File:** `/Users/benjamincrane/service-engine-x/service-engine-x-api/app/config.py`

**Pydantic Settings class** (inherited from `BaseAuthSettings`):

```python
class Settings(BaseAuthSettings):
    # ... other settings ...
    
    # Third-party
    RESEND_API_KEY: str = ""
    DOCRAPTOR_API_KEY: str = ""
    CAL_API_KEY: str = ""
    CALCOM_BASE_URL: str = "https://api.cal.com"
    CALCOM_API_VERSION: str = "2024-06-14"
    CALCOM_EVENT_TYPE_CACHE_TTL_SECONDS: int = 86400
    CAL_WEBHOOK_SECRET: str = ""
```

### Webhook-related env vars
1. **CAL_WEBHOOK_SECRET** (string, optional)
   - Purpose: HMAC-SHA256 secret for verifying `X-Cal-Signature-256` header
   - Default: `""` (empty string = verification skipped, local dev mode)
   - Used in: `cal_webhooks.py._verify_signature()`
   - Behavior: If not set, logs warning and returns True (skips verification)

### Cal.com API-related env vars (not directly used by webhook handler)
2. **CAL_API_KEY** (string, optional)
   - Purpose: Bearer token for Cal.com API calls
   - Default: `""` (empty)

3. **CALCOM_BASE_URL** (string, optional)
   - Purpose: Base URL for Cal.com API
   - Default: `"https://api.cal.com"`

4. **CALCOM_API_VERSION** (string, optional)
   - Purpose: API version for Cal.com requests
   - Default: `"2024-06-14"`

5. **CALCOM_EVENT_TYPE_CACHE_TTL_SECONDS** (integer)
   - Purpose: TTL for event type metadata cache
   - Default: `86400` (24 hours)

### Inherited from BaseAuthSettings (AUX M2M)
- `AUX_JWKS_URL`
- `AUX_ISSUER`
- `AUX_AUDIENCE`
- `AUX_API_BASE_URL`
- `AUX_M2M_API_KEY`

### Database env vars
- `SERVICE_ENGINE_X_SUPABASE_URL` (from Settings class)
- `SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY` (from Settings class)

---

## 8. Gotchas

### Dual payload shapes
**Quirk:** MEETING_STARTED and MEETING_ENDED events use a flat payload structure, while all other Cal.com webhook events nest the booking data under a `payload` key.

**Code reference:** `cal_webhooks.py`, lines 26-28:
```python
FLAT_PAYLOAD_TRIGGERS = {"MEETING_STARTED", "MEETING_ENDED"}
```

**Impact:** Extracting fields (uid, hosts, attendees, eventTypeId) must check both top-level and nested `payload` object.

---

### HMAC verification uses raw body
**Quirk:** The HMAC signature is computed over the raw request body (as bytes), not the parsed JSON. This is critical for verification.

**Code reference:** `cal_webhooks.py`, lines 98, 101-102, 45-47:
```python
raw_body = await request.body()  # bytes
signature = request.headers.get("X-Cal-Signature-256")
if not _verify_signature(raw_body, signature):  # raw_body passed as bytes
    ...
    
def _verify_signature(raw_body: bytes, signature_header: str | None) -> bool:
    ...
    expected = hmac.new(
        secret.encode(), raw_body, hashlib.sha256
    ).hexdigest()
```

**Impact:** Any JSON formatting changes (whitespace, key order) will invalidate the signature. Must use raw bytes for verification.

---

### Unhandled events are silently stored
**Quirk:** When an event type has no registered handler in `_ROUTED_EVENTS`, it is logged as "unhandled" but still stored in `cal_raw_events`.

**Code reference:** `cal_event_handlers.py`, lines 34-42:
```python
def route_cal_event(event_row: dict[str, Any]) -> None:
    """Dispatch an event row to the appropriate handler, or log as unhandled."""
    trigger = event_row.get("trigger_event", "unknown")
    event_id = event_row.get("id", "?")

    handler_entry = _ROUTED_EVENTS.get(trigger)
    if handler_entry is None:
        logger.info("unhandled trigger=%s id=%s — stored only", trigger, event_id)
        return
```

**Impact:** Events like BOOKING_REQUESTED, RECORDING_READY, etc. are captured in the database but do not dispatch to any agent until handlers are registered.

---

### Deliberate duplicate allowance for replay safety
**Quirk:** `cal_booking_events` table intentionally allows duplicate rows (no UNIQUE constraint). Comment at line 422 in `internal_cal_events.py` states:
```python
# Deliberately allowing duplicate booking lifecycle events for auditability/replay safety.
```

**Code reference:** `internal_cal_events.py`, line 422-423:
```python
# Deliberately allowing duplicate booking lifecycle events for auditability/replay safety.
result = supabase.table("cal_booking_events").insert(payload).execute()
```

**Impact:** The same webhook can be replayed multiple times without causing INSERT errors. Deduplication is expected to happen downstream in handlers or at the application layer.

---

### Attendee upsert on (uid, email, role)
**Quirk:** `cal_booking_attendees` uses UPSERT with conflict on `(cal_booking_uid, email, role)`, meaning the same person can appear twice in a booking if they have different roles (e.g., as both attendee and host).

**Code reference:** `internal_cal_events.py`, lines 528-530:
```python
result = (
    supabase.table("cal_booking_attendees")
    .upsert(upserts, on_conflict="cal_booking_uid,email,role")
    .execute()
)
```

**Migration reference:** `014_replace_calcom_webhook_log_with_cal_normalization_tables.sql`, lines 105-106:
```sql
ALTER TABLE cal_booking_attendees
    ADD CONSTRAINT uq_cal_booking_attendees_uid_email_role
    UNIQUE (cal_booking_uid, email, role);
```

**Impact:** Bulk attendee updates re-process the entire attendee list safely without duplicates per role.

---

### Empty CAL_WEBHOOK_SECRET skips HMAC verification
**Quirk:** If the `CAL_WEBHOOK_SECRET` environment variable is not set or is empty, webhook signature verification is skipped entirely.

**Code reference:** `cal_webhooks.py`, lines 35-39:
```python
secret = settings.CAL_WEBHOOK_SECRET
if not secret:
    logger.warning("CAL_WEBHOOK_SECRET not set — skipping HMAC verification")
    return True
```

**Impact:** In local development without the secret configured, any payload will be accepted. In production, misconfiguration would allow spoofed webhooks.

---

### Event type field variation
**Quirk:** The trigger event field can come from either `triggerEvent` (standard) or `type` (fallback) in the payload.

**Code reference:** `internal_cal_events.py`, lines 54-56:
```python
def _extract_trigger_event(payload: dict[str, Any]) -> str:
    trigger_event = payload.get("triggerEvent") or payload.get("type")
    return str(trigger_event) if trigger_event else "UNKNOWN"
```

**Impact:** Payloads with a `type` field instead of `triggerEvent` will still be recognized.

---

### Booking UID extraction tries multiple paths
**Quirk:** Booking UID extraction checks four different paths:
1. `payload.uid` (nested in envelope)
2. `payload` → `payload.uid` (nested in nested payload)
3. Top-level `uid`
4. Top-level `payload.uid` again (fallback)

**Code reference:** `internal_cal_events.py`, lines 59-68:
```python
def _extract_booking_uid(payload: dict[str, Any]) -> str | None:
    nested = payload.get("payload")
    if isinstance(nested, dict):
        uid = nested.get("uid")
        if isinstance(uid, str) and uid.strip():
            return uid.strip()
    top_uid = payload.get("uid")
    if isinstance(top_uid, str) and top_uid.strip():
        return top_uid.strip()
    return None
```

**Impact:** Handles multiple payload schema variations gracefully.

---

### Date parsing accepts 'Z' suffix
**Quirk:** DateTime parsing in `_parse_dt()` handles ISO 8601 strings with or without the 'Z' timezone indicator.

**Code reference:** `internal_cal_events.py`, lines 35-41:
```python
def _parse_dt(value: Any) -> str | None:
    if not value or not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
    except ValueError:
        return None
```

**Impact:** Both `2024-01-01T12:00:00Z` and `2024-01-01T12:00:00+00:00` formats are accepted.

---

### Email normalization (lowercase + strip)
**Quirk:** All email addresses extracted from attendees/hosts are lowercased and whitespace-stripped.

**Code reference:** `internal_cal_events.py`, lines 165, 185:
```python
"email": email.strip().lower(),
```

And in bulk attendee upsert, line 518:
```python
"email": attendee.get("email").strip().lower(),
```

**Impact:** Attendee queries must use lowercase emails to match stored records.

---

### Legacy immutable audit log (cal_webhook_events_raw)
**Quirk:** The `cal_webhook_events_raw` table (used by the legacy `calcom_webhooks.py` sink) has an immutability trigger that prevents updates to all fields except `processed_at`.

**Code reference:** `014_replace_calcom_webhook_log_with_cal_normalization_tables.sql`, lines 29-49:
```sql
CREATE OR REPLACE FUNCTION enforce_cal_webhook_events_raw_immutability()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.trigger_event IS DISTINCT FROM OLD.trigger_event
       OR NEW.payload IS DISTINCT FROM OLD.payload
       OR NEW.org_id IS DISTINCT FROM OLD.org_id
       OR NEW.cal_booking_uid IS DISTINCT FROM OLD.cal_booking_uid
       OR NEW.received_at IS DISTINCT FROM OLD.received_at THEN
        RAISE EXCEPTION 'cal_webhook_events_raw is immutable; only processed_at can be updated';
    END IF;
    RETURN NEW;
END;
$$;
```

**Impact:** The legacy sink is for audit purposes only; no mutations allowed except marking processed.

---

### Two separate receiver endpoints
**Quirk:** Two separate Cal.com webhook receiver endpoints exist:
1. `/api/webhooks/cal` — Primary, HMAC-verified, routable to agents
2. `/api/webhooks/calcom` — Legacy, no verification, immutable audit log only

**Code reference:** 
- Primary: `cal_webhooks.py`, line 95
- Legacy: `calcom_webhooks.py`, line 11

**Impact:** Webhooks must be configured to send to the correct endpoint. The primary endpoint is recommended for new integrations.

---

### No explicit request timeout
**Quirk:** The webhook handler does not set an explicit timeout for the Supabase insert operation.

**Code reference:** `cal_webhooks.py`, lines 114-125:
```python
result = supabase.table("cal_raw_events").insert(row).execute()
```

**Impact:** If Supabase is slow, the webhook will hang (FastAPI defaults to ~5 minute timeout). Downstream agent dispatch may time out if the database insert is slow.

---

### cal_webhook_agent_routes is a configuration table
**Quirk:** The `cal_webhook_agent_routes` table is not automatically populated by the webhook handler; it is a configuration table managed separately (via migrations 017 and 018).

**Code reference:** `017_cal_webhook_agent_routes.sql`, lines 18-38 (INSERT statements with hardcoded agent IDs)

**Impact:** To route a new event type, the table must be manually populated with agent IDs. The webhook handler only reads this table for dispatch decisions (if implemented in downstream Pipedream logic).

---

### Provider slug standardization (cal.com → cal_com)
**Quirk:** Migration 021 renames the provider slug from `"cal.com"` to `"cal_com"` in the `accounts` and `deals` tables.

**Code reference:** `021_rename_cal_com_source_to_cal_com.sql`, lines 10-11:
```sql
UPDATE accounts SET source = 'cal_com' WHERE source = 'cal.com';
UPDATE deals    SET source = 'cal_com' WHERE source = 'cal.com';
```

**Impact:** Any code checking `source == 'cal.com'` will fail post-migration. Use `'cal_com'` instead.

---

### Stub handlers are TODO (no actual agent dispatch)
**Quirk:** All registered handlers in `cal_event_handlers.py` are stubs with TODO comments awaiting implementation of actual Anthropic managed agent session creation.

**Code reference:** `cal_event_handlers.py`, lines 53-70 (BOOKING_CREATED example):
```python
@_register("BOOKING_CREATED", agent_type="booking_created_agent")
def handle_booking_created(event_row: dict[str, Any]) -> None:
    event_id = event_row.get("id")
    logger.info("BOOKING_CREATED handler — event_id=%s", event_id)

    # ---------------------------------------------------------------
    # TODO: Create managed agent session (Anthropic API)
    #
    # from anthropic import Anthropic
    # client = Anthropic()
    # session = client.beta.sessions.create(
    #     model="claude-sonnet-4-20250514",
    #     instructions="...",
    #     tools=[...],
    # )
    # ---------------------------------------------------------------

    _mark_processed(event_id, "booking_created_agent")
```

**Impact:** Currently, handlers only mark events as processed; no downstream business logic (sales agent, notification, deal creation) is executed.

---

## 9. Testing

### Test files
No dedicated test files found in the repository (glob search for test*cal*.py returned no results).

### Integration test hints
**File:** `/Users/benjamincrane/service-engine-x/service-engine-x-api/app/routers/internal_cal_events.py`

This file contains the internal API for querying and creating cal.com events, which can be used for integration testing:
- `POST /api/internal/cal/events/raw` — Create a raw event manually
- `GET /api/internal/cal/events/raw/unprocessed` — List unprocessed events
- `POST /api/internal/cal/booking-events` — Create a booking event
- `POST /api/internal/cal/booking-attendees/bulk` — Bulk upsert attendees
- `POST /api/internal/cal/recordings` — Create a recording

### Example test scenarios (based on code structure)
1. **HMAC verification:** Send requests with invalid signatures and verify 401 response
2. **Dual payload shapes:** Test MEETING_STARTED (flat) and BOOKING_CREATED (envelope) payloads
3. **Field extraction:** Verify all fields are correctly parsed from both shapes
4. **Attendee normalization:** Test attendee list parsing and email lowercasing
5. **Event routing:** Verify events are routed to correct handlers and marked as processed
6. **Unhandled events:** Test that unrouted events are stored but not dispatched
7. **Duplicate handling:** Send the same webhook twice and verify idempotency via UPSERT

---

## 10. Gotchas (continued from section 8)

### Comments in code mentioning Cal.com
**Code reference:** `/Users/benjamincrane/service-engine-x/service-engine-x-api/app/main.py`, lines 164-165:
```python
app.include_router(cal_webhooks_router)  # Cal.com webhook receiver (HMAC + agent routing)
app.include_router(calcom_webhooks_router)  # Cal.com legacy webhook sink (raw capture)
```

**Reference docs comment:** `cal_webhooks.py`, line 6:
```python
# See: api-reference-docs-new/cal.com/CALCOM-WEBHOOKS.md for payload specs.
```

(Note: This file path no longer exists in the main codebase but is referenced in worktrees)

---

## Summary of Key Points

1. **Two receivers:** Primary (`/api/webhooks/cal`) with HMAC + agent routing, legacy (`/api/webhooks/calcom`) for audit only
2. **HMAC-SHA256** over raw bytes; secret from `CAL_WEBHOOK_SECRET` env var
3. **Dual payload shapes:** Standard envelope for most events, flat shape for MEETING_STARTED/MEETING_ENDED
4. **Raw storage:** Full payload stored in `cal_raw_events` table as JSONB
5. **Normalization:** Fields extracted into separate tables (cal_booking_events, cal_booking_attendees, cal_recordings) via internal API
6. **Event routing:** Events routed to registered handlers via decorator pattern; unhandled events logged and stored only
7. **Replay safety:** Deliberate duplicate allowance in cal_booking_events; UPSERT on (uid, email, role) for attendees
8. **Stub handlers:** All registered handlers are TODO stubs awaiting Anthropic managed agent integration
9. **No explicit deduplication/idempotency:** Downstream handlers expected to implement replay protection
10. **Configuration table:** `cal_webhook_agent_routes` maps events to Pipedream agent IDs (externally managed)

