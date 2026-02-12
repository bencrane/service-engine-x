-- Migration: Add systems and system_access tables for Everything Automation
-- Run: psql $DATABASE_URL -f migrations/005_add_systems.sql

-- Systems catalog (what you sell / provide access to)
CREATE TABLE IF NOT EXISTS systems (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  price NUMERIC(12,2),
  currency VARCHAR(3) NOT NULL DEFAULT 'USD',
  public BOOLEAN NOT NULL DEFAULT true,
  sort_order INTEGER NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_systems_org_id ON systems(org_id);
CREATE INDEX IF NOT EXISTS idx_systems_deleted_at ON systems(deleted_at) WHERE deleted_at IS NULL;

-- System access (who has access to what)
CREATE TABLE IF NOT EXISTS system_access (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  system_id UUID NOT NULL REFERENCES systems(id) ON DELETE CASCADE,
  client_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  engagement_id UUID REFERENCES engagements(id) ON DELETE SET NULL,
  status INTEGER NOT NULL DEFAULT 1,  -- 1=active, 2=suspended, 3=revoked
  granted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_system_access_org_id ON system_access(org_id);
CREATE INDEX IF NOT EXISTS idx_system_access_system_id ON system_access(system_id);
CREATE INDEX IF NOT EXISTS idx_system_access_client_id ON system_access(client_id);
CREATE INDEX IF NOT EXISTS idx_system_access_status ON system_access(status);
