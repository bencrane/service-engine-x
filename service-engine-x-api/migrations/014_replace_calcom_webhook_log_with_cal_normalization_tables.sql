-- Replace legacy calcom_webhook_log with normalized Cal.com event pipeline tables.
-- Note: calcom_webhook_log currently contains test/dev rows; this migration intentionally drops it.

DROP TABLE IF EXISTS calcom_webhook_log;

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

COMMENT ON TABLE cal_webhook_events_raw IS
'Immutable append-only Cal.com webhook log; only processed_at may be updated.';

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

COMMENT ON TABLE cal_booking_events IS
'Normalized Cal.com booking lifecycle events. Duplicates are allowed by design.';

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

COMMENT ON TABLE cal_booking_attendees IS
'Attendees and hosts per booking; guests are stored as email strings on cal_booking_events.guests.';

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

COMMENT ON TABLE cal_recordings IS
'Cal.com recording metadata from RECORDING_READY events, keyed by recording id.';
