-- Add task_instruction_template column to cal_webhook_agent_routes.
-- Pipedream renders this template (with placeholders like {raw_event_id}, {org_id}, {trigger_event})
-- into the user message that dispatches the managed agent for each event type.

ALTER TABLE cal_webhook_agent_routes
    ADD COLUMN task_instruction_template TEXT;

COMMENT ON COLUMN cal_webhook_agent_routes.task_instruction_template IS
'User-message template dispatched to the managed agent. Supports placeholders like {raw_event_id}, {org_id}, {trigger_event} rendered by the Pipedream worker.';

UPDATE cal_webhook_agent_routes
SET task_instruction_template =
'Dispatch for BOOKING_CREATED.
raw_event_id: {raw_event_id}
org_id: {org_id}
trigger_event: BOOKING_CREATED
Execute the new-booking pipeline per your system prompt.'
WHERE event_name = 'BOOKING_CREATED';
