-- 019_scheduler_preframe.sql
-- Additions for the SERX time-based event scheduler.
--
-- meetings.preframe_sent_at — orchestrator writes this on successful preframe
-- send; scheduler uses it as the authoritative "don't re-dispatch" signal.
--
-- Idempotency for the scheduler's synthetic webhook_events_raw rows is
-- handled by the existing (source, event_key) unique constraint on that
-- table (owned by serx-webhooks). The scheduler writes
-- event_key = 'serx_scheduler:<event_name>:<meeting_id>', so overlapping
-- ticks surface as duplicate-key violations and are caught in the router.

ALTER TABLE meetings
    ADD COLUMN IF NOT EXISTS preframe_sent_at TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS idx_meetings_preframe_due
    ON meetings (start_time)
    WHERE status = 'scheduled' AND preframe_sent_at IS NULL;

COMMENT ON COLUMN meetings.preframe_sent_at IS
    'Set by the meeting-preframe-orchestrator after the preframe email lands. '
    'Scheduler skips meetings where this is non-null.';
