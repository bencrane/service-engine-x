-- Agent-routable Cal.com webhook event log.
-- Sits alongside cal_webhook_events_raw (immutable audit log) —
-- this table tracks processing state for agent dispatch.

BEGIN;

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

COMMENT ON TABLE cal_raw_events IS
'Cal.com webhook events stored for agent routing. processed/processed_by track dispatch state.';

COMMIT;
