-- Migration: 002_add_proposals_system.sql
-- Description: Create proposals system for Service-Engine-X
-- Date: 2026-02-07

-- ============================================
-- 1. CREATE PROPOSALS TABLE
-- ============================================

CREATE TABLE proposals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  client_email VARCHAR(255) NOT NULL,
  client_name_f VARCHAR(100) NOT NULL,
  client_name_l VARCHAR(100) NOT NULL,
  client_company VARCHAR(255),
  status INTEGER NOT NULL DEFAULT 0,  -- 0=draft, 1=sent, 2=signed, 3=rejected
  total DECIMAL(10,2) NOT NULL,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  sent_at TIMESTAMPTZ,
  signed_at TIMESTAMPTZ,
  converted_order_id UUID REFERENCES orders(id) ON DELETE SET NULL,
  deleted_at TIMESTAMPTZ
);

COMMENT ON TABLE proposals IS 'Sales proposals that can be sent to clients for signing';
COMMENT ON COLUMN proposals.status IS '0=draft, 1=sent, 2=signed, 3=rejected';

-- ============================================
-- 2. CREATE PROPOSAL_ITEMS TABLE
-- ============================================

CREATE TABLE proposal_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  proposal_id UUID NOT NULL REFERENCES proposals(id) ON DELETE CASCADE,
  service_id UUID NOT NULL REFERENCES services(id) ON DELETE RESTRICT,
  quantity INTEGER NOT NULL DEFAULT 1,
  price DECIMAL(10,2) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE proposal_items IS 'Line items on a proposal, linked to services';

-- ============================================
-- 3. CREATE INDEXES
-- ============================================

-- Index for filtering proposals by organization
CREATE INDEX idx_proposals_org_id ON proposals(org_id);

-- Composite index for filtering by org and status (common query pattern)
CREATE INDEX idx_proposals_status ON proposals(org_id, status) WHERE deleted_at IS NULL;

-- Index for looking up items by proposal
CREATE INDEX idx_proposal_items_proposal ON proposal_items(proposal_id);

-- Index for looking up proposals by client email within an org
CREATE INDEX idx_proposals_client_email ON proposals(org_id, client_email) WHERE deleted_at IS NULL;

-- ============================================
-- 4. VERIFICATION
-- ============================================

-- Verify tables were created
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'proposals') THEN
    RAISE EXCEPTION 'proposals table was not created';
  END IF;

  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'proposal_items') THEN
    RAISE EXCEPTION 'proposal_items table was not created';
  END IF;

  RAISE NOTICE 'Migration 002_add_proposals_system completed successfully';
END $$;
