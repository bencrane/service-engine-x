-- Rename provider slug "cal.com" -> "cal_com" in existing rows.
--
-- We standardized on underscore-separated provider identifiers so they
-- are safe to use in code paths, log labels, and URL segments without
-- escaping. Only updates rows with the exact prior value; any downstream
-- tables we discover later can get their own migration.

BEGIN;

UPDATE accounts SET source = 'cal_com' WHERE source = 'cal.com';
UPDATE deals    SET source = 'cal_com' WHERE source = 'cal.com';

COMMIT;
