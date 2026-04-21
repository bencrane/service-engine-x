create table if not exists webhook_events_raw (
    id uuid primary key default gen_random_uuid(),
    source text not null,
    trigger_event text,
    event_key text not null,
    payload jsonb not null,
    raw_body bytea not null,
    headers jsonb,
    signature_valid boolean,
    status text not null default 'received'
        check (status in ('received', 'processed', 'failed', 'dead_letter')),
    received_at timestamptz not null default now(),
    constraint webhook_events_raw_source_event_key_unique
        unique (source, event_key)
);

create index if not exists webhook_events_raw_source_event_received_idx
    on webhook_events_raw (source, trigger_event, received_at desc);

create index if not exists webhook_events_raw_status_received_idx
    on webhook_events_raw (status, received_at desc);
