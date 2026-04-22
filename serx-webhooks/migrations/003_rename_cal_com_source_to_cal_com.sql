-- Rename provider slug "cal.com" -> "cal_com" in webhook_events_raw.
--
-- Matches the cross-repo rename so downstream consumers (including the
-- managed-agents dispatcher built in migration 002) see a single
-- underscore-separated provider identifier.

BEGIN;

UPDATE webhook_events_raw SET source = 'cal_com' WHERE source = 'cal.com';

COMMIT;
