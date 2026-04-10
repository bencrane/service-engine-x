-- Meetings + Deals pipeline foundation for Cal.com-driven sales flow.
-- Adds deals, meetings, and event type cache tables.

CREATE TABLE deals (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id                  UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    account_id              UUID REFERENCES accounts(id) ON DELETE SET NULL,
    contact_id              UUID REFERENCES contacts(id) ON DELETE SET NULL,
    proposal_id             UUID REFERENCES proposals(id) ON DELETE SET NULL,
    title                   VARCHAR(255) NOT NULL,
    status                  VARCHAR(20) NOT NULL DEFAULT 'qualified',
    value                   DECIMAL(12,2),
    source                  VARCHAR(50),
    referred_by_account_id  UUID REFERENCES accounts(id) ON DELETE SET NULL,
    lost_reason             TEXT,
    notes                   TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at               TIMESTAMPTZ,
    deleted_at              TIMESTAMPTZ,
    CONSTRAINT deals_status_check
        CHECK (status IN ('qualified', 'proposal_sent', 'negotiating', 'won', 'lost'))
);

CREATE INDEX idx_deals_org_id ON deals(org_id);
CREATE INDEX idx_deals_account_id ON deals(account_id);
CREATE INDEX idx_deals_contact_id ON deals(contact_id);
CREATE INDEX idx_deals_proposal_id ON deals(proposal_id);
CREATE INDEX idx_deals_status ON deals(status);
CREATE INDEX idx_deals_source ON deals(source);
CREATE INDEX idx_deals_deleted_at ON deals(deleted_at) WHERE deleted_at IS NULL;

COMMENT ON TABLE deals IS 'Sales opportunities created from qualified meetings.';

CREATE TABLE meetings (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id              UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    account_id          UUID REFERENCES accounts(id) ON DELETE SET NULL,
    contact_id          UUID REFERENCES contacts(id) ON DELETE SET NULL,
    deal_id             UUID REFERENCES deals(id) ON DELETE SET NULL,
    cal_event_uid       VARCHAR(255),
    cal_booking_id      BIGINT,
    title               VARCHAR(255) NOT NULL,
    start_time          TIMESTAMPTZ NOT NULL,
    end_time            TIMESTAMPTZ NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    organizer_email     VARCHAR(255),
    attendee_emails     JSONB NOT NULL DEFAULT '[]'::jsonb,
    notes               TEXT,
    recording_url       TEXT,
    transcript_url      TEXT,
    host_no_show        BOOLEAN NOT NULL DEFAULT FALSE,
    guest_no_show       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT meetings_status_check
        CHECK (status IN ('pending', 'scheduled', 'in_progress', 'completed', 'cancelled', 'rejected', 'no_show', 'rescheduled'))
);

CREATE UNIQUE INDEX idx_meetings_cal_event_uid_unique
    ON meetings(cal_event_uid)
    WHERE cal_event_uid IS NOT NULL;

CREATE UNIQUE INDEX idx_meetings_cal_booking_id_unique
    ON meetings(cal_booking_id)
    WHERE cal_booking_id IS NOT NULL;

CREATE INDEX idx_meetings_org_id ON meetings(org_id);
CREATE INDEX idx_meetings_deal_id ON meetings(deal_id);
CREATE INDEX idx_meetings_account_id ON meetings(account_id);
CREATE INDEX idx_meetings_contact_id ON meetings(contact_id);
CREATE INDEX idx_meetings_status ON meetings(status);
CREATE INDEX idx_meetings_start_time ON meetings(start_time DESC);
CREATE INDEX idx_meetings_attendee_emails_gin ON meetings USING GIN (attendee_emails);

COMMENT ON TABLE meetings IS 'Calendar meetings with prospects, optionally linked to deals.';

CREATE TABLE cal_event_type_cache (
    event_type_id    BIGINT PRIMARY KEY,
    org_id           UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    cal_team_id      INTEGER NOT NULL,
    event_type_slug  TEXT,
    event_type_title TEXT,
    raw_response     JSONB NOT NULL DEFAULT '{}'::jsonb,
    refreshed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cal_event_type_cache_org_id ON cal_event_type_cache(org_id);
CREATE INDEX idx_cal_event_type_cache_team_id ON cal_event_type_cache(cal_team_id);
CREATE INDEX idx_cal_event_type_cache_refreshed_at ON cal_event_type_cache(refreshed_at DESC);

COMMENT ON TABLE cal_event_type_cache IS 'Cache of Cal.com eventTypeId to team/org resolution.';
