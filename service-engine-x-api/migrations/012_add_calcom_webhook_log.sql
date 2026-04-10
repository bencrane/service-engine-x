-- Stores raw Cal.com webhook payloads for inspection.
-- No org scoping — this is a dev/debug capture table.

CREATE TABLE calcom_webhook_log (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type  VARCHAR(100),
    payload     JSONB NOT NULL,
    headers     JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE calcom_webhook_log IS 'Raw Cal.com webhook payloads for development inspection.';
