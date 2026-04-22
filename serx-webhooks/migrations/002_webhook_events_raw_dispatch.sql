-- Dispatch webhook_events_raw rows to managed-agents-x-api.
--
-- After persisting an inbound webhook, serx-webhooks POSTs an event_ref
-- to managed-agents-x-api /sessions/from-event so a managed agent session
-- is created. Dispatch outcome is recorded on the row itself. Mirrors the
-- OEX webhook_events dispatch column family (migration 080) so cross-service
-- runbooks can treat both the same way.

BEGIN;

ALTER TABLE webhook_events_raw
    ADD COLUMN IF NOT EXISTS dispatch_status TEXT;

ALTER TABLE webhook_events_raw
    ADD COLUMN IF NOT EXISTS dispatched_session_id TEXT;

ALTER TABLE webhook_events_raw
    ADD COLUMN IF NOT EXISTS dispatched_at TIMESTAMPTZ;

ALTER TABLE webhook_events_raw
    ADD COLUMN IF NOT EXISTS dispatch_error TEXT;

ALTER TABLE webhook_events_raw
    DROP CONSTRAINT IF EXISTS webhook_events_raw_dispatch_status_check;

ALTER TABLE webhook_events_raw
    ADD CONSTRAINT webhook_events_raw_dispatch_status_check
    CHECK (
        dispatch_status IS NULL
        OR dispatch_status IN (
            'pending',
            'dispatched',
            'dispatched_skipped',
            'dispatch_disabled',
            'dispatch_failed'
        )
    );

CREATE INDEX IF NOT EXISTS webhook_events_raw_dispatch_unresolved_idx
    ON webhook_events_raw (source, dispatch_status, received_at DESC)
    WHERE dispatch_status IS NOT NULL
      AND dispatch_status NOT IN ('dispatched', 'dispatched_skipped');

COMMIT;
