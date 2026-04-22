-- Adds a flexible custom_fields JSONB to meetings so Cal.com booking form answers
-- (and future non-Cal sources) can flow in without schema migrations per new question.
-- Core identity fields (name, email, phone, company) still go to structured columns
-- on contacts / accounts. Everything else lands here.

ALTER TABLE meetings
    ADD COLUMN custom_fields JSONB NOT NULL DEFAULT '{}'::jsonb;

COMMENT ON COLUMN meetings.custom_fields IS
'Freeform per-booking context from the source form (e.g. Cal.com responses). Core fields belong on contacts/accounts; this is for the rest.';
