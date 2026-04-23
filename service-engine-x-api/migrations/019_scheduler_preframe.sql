-- 019_scheduler_preframe.sql
-- Additions for the SERX time-based event scheduler.
--
-- 1. meetings.preframe_sent_at — orchestrator writes this on successful preframe
--    send; scheduler uses it as the authoritative "don't re-dispatch" signal.
-- 2. webhook_events_raw unique partial index — DB-level idempotency guard so
--    overlapping scheduler ticks cannot double-insert the same
--    (source='serx_scheduler', event_name, payload.meeting_id) tuple.
--
-- The webhook_events_raw table itself is owned by serx-webhooks-ingest.
-- This migration only adds an index; column schema is unchanged.

ALTER TABLE meetings
    ADD COLUMN IF NOT EXISTS preframe_sent_at TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS idx_meetings_preframe_due
    ON meetings (start_time)
    WHERE status = 'scheduled' AND preframe_sent_at IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_webhook_events_raw_serx_scheduler_meeting
    ON webhook_events_raw (event_name, (payload->>'meeting_id'))
    WHERE source = 'serx_scheduler';

COMMENT ON COLUMN meetings.preframe_sent_at IS
    'Set by the meeting-preframe-orchestrator after the preframe email lands. '
    'Scheduler skips meetings where this is non-null.';

COMMENT ON INDEX uq_webhook_events_raw_serx_scheduler_meeting IS
    'Idempotency guard for the SERX scheduler. Prevents duplicate dispatch '
    'rows for the same (event_name, meeting_id) from overlapping ticks.';
