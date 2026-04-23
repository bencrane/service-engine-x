-- Maps Cal.com webhook trigger_event values to a managed agent for Pipedream routing.
-- Pipedream reads from this table to decide which agent (if any) to invoke for an incoming webhook.

CREATE TABLE cal_webhook_agent_routes (
    event_name       TEXT PRIMARY KEY,
    description      TEXT,
    agent_id         TEXT,
    environment_id   TEXT NOT NULL,
    credential_vault TEXT NOT NULL,
    enabled          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE cal_webhook_agent_routes IS
'Maps Cal.com webhook trigger_event to a managed agent for Pipedream routing. NULL agent_id = no handler yet.';

INSERT INTO cal_webhook_agent_routes (event_name, description, agent_id, environment_id, credential_vault) VALUES
    ('BOOKING_CREATED',                   'New booking created',                                 'agent_011CZtixhAnM2rgE68RbSbTA', 'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E'),
    ('BOOKING_REQUESTED',                 'Booking requires manual confirmation (pending)',      NULL,                              'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E'),
    ('BOOKING_RESCHEDULED',               'Existing booking rescheduled to new time',            'agent_011CZvtd69ztjNr4FdDsxbsx', 'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E'),
    ('BOOKING_CANCELLED',                 'Booking cancelled by host or attendee',               'agent_011CZvrV7PxgxUBi49DfwZzF', 'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E'),
    ('BOOKING_REJECTED',                  'Pending booking rejected by host',                    'agent_011CZvtgrR7qc1D845Tc8Rbo', 'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E'),
    ('BOOKING_NO_SHOW_UPDATED',           'No-show status updated (mark-absent)',                NULL,                              'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E'),
    ('BOOKING_PAYMENT_INITIATED',         'Payment process started',                             NULL,                              'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E'),
    ('BOOKING_PAID',                      'Payment completed',                                   NULL,                              'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E'),
    ('INSTANT_MEETING',                   'Instant meeting created (team event types)',          NULL,                              'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E'),
    ('MEETING_STARTED',                   'Cal Video meeting started (flat payload)',            NULL,                              'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E'),
    ('MEETING_ENDED',                     'Cal Video meeting ended (flat payload)',              NULL,                              'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E'),
    ('RECORDING_READY',                   'Cal Video recording ready for download',              NULL,                              'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E'),
    ('RECORDING_TRANSCRIPTION_GENERATED', 'Cal Video transcription generated',                   NULL,                              'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E'),
    ('AFTER_HOSTS_CAL_VIDEO_NO_SHOW',     'Host didn''t join Cal Video',                         NULL,                              'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E'),
    ('AFTER_GUESTS_CAL_VIDEO_NO_SHOW',    'Guest didn''t join Cal Video',                        NULL,                              'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E'),
    ('FORM_SUBMITTED',                    'Routing form submitted (event created)',              NULL,                              'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E'),
    ('FORM_SUBMITTED_NO_EVENT',           'Routing form submitted (no event created)',           NULL,                              'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E'),
    ('ROUTING_FORM_FALLBACK_HIT',         'Routing form hit fallback route',                     NULL,                              'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E'),
    ('OOO_CREATED',                       'Out-of-office entry created',                         NULL,                              'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E'),
    ('DELEGATION_CREDENTIAL_ERROR',       'Delegation credential error',                         NULL,                              'env_01T3cywTrvvtZoUQYAzxMA1D', 'vlt_011CZtjQ5LjLrbAd4gX7xA6E');
