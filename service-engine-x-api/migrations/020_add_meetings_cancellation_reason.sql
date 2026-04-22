-- Optional free-text reason captured from BOOKING_CANCELLED webhook payloads
-- (e.g. Cal.com cancellationReason). Nullable; agents must not fail if absent.

ALTER TABLE meetings
    ADD COLUMN cancellation_reason TEXT;

COMMENT ON COLUMN meetings.cancellation_reason IS
'Optional free-text reason captured from BOOKING_CANCELLED webhook payloads (e.g. Cal.com cancellationReason).';
