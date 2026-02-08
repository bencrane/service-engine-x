-- ============================================================================
-- MIGRATION: Add Multi-Tenant Support to Service-Engine-X
-- ============================================================================
--
-- Purpose: Enable organization-level data isolation so multiple businesses
--          (Revenue Activation, Outbound Solutions) can operate independently.
--
-- Created: 2026-02-07
--
-- IMPORTANT: Run this in Supabase SQL Editor as a single transaction.
--            Review the existing user IDs before running to ensure they match.
--
-- Current Database State:
--   - 2 roles (Administrator, Client)
--   - 2 users (team@revenueactivation.com, team@outboundsolutions.com)
--   - 1 API token (for revenueactivation.com user)
--   - 3 sessions
--   - All business tables empty (services, orders, invoices, etc.)
--
-- ============================================================================

BEGIN;

-- ============================================================================
-- STEP 1: Create Organizations Table
-- ============================================================================
-- This is the foundation for multi-tenancy. Every resource will reference
-- an organization via org_id.

CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for slug lookups (used in URLs, API routing)
CREATE INDEX IF NOT EXISTS idx_organizations_slug ON organizations(slug);

COMMENT ON TABLE organizations IS 'Multi-tenant organizations. Each org has isolated data.';
COMMENT ON COLUMN organizations.slug IS 'URL-safe identifier (e.g., revenue-activation)';

-- ============================================================================
-- STEP 2: Seed Organizations
-- ============================================================================
-- Create the two initial organizations with deterministic UUIDs for easy reference.

INSERT INTO organizations (id, name, slug) VALUES
    ('11111111-1111-1111-1111-111111111111', 'Revenue Activation', 'revenue-activation'),
    ('22222222-2222-2222-2222-222222222222', 'Outbound Solutions', 'outbound-solutions')
ON CONFLICT (slug) DO NOTHING;

-- ============================================================================
-- STEP 3: Add org_id Column to Users Table
-- ============================================================================
-- Users belong to an organization. Team members and clients are org-scoped.

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id) ON DELETE RESTRICT;

-- Assign existing users to their organizations based on email domain
UPDATE users
SET org_id = '11111111-1111-1111-1111-111111111111'
WHERE email = 'team@revenueactivation.com';

UPDATE users
SET org_id = '22222222-2222-2222-2222-222222222222'
WHERE email = 'team@outboundsolutions.com';

-- Now make org_id NOT NULL (all existing users have been assigned)
ALTER TABLE users
    ALTER COLUMN org_id SET NOT NULL;

-- Index for org-scoped queries
CREATE INDEX IF NOT EXISTS idx_users_org_id ON users(org_id);

-- Composite index for common query pattern: list users in an org
CREATE INDEX IF NOT EXISTS idx_users_org_role ON users(org_id, role_id);

COMMENT ON COLUMN users.org_id IS 'Organization this user belongs to. Required for all users.';

-- ============================================================================
-- STEP 4: Add org_id Column to API Tokens Table
-- ============================================================================
-- API tokens are scoped to an organization. Token validation returns org_id.

ALTER TABLE api_tokens
    ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

-- Update existing API token to belong to Revenue Activation
-- (The token belongs to user_id = 090c00f6-3b50-4382-8310-1be9c3fe7744 which is RA)
UPDATE api_tokens
SET org_id = '11111111-1111-1111-1111-111111111111'
WHERE user_id IN (
    SELECT id FROM users WHERE email = 'team@revenueactivation.com'
);

-- Make org_id NOT NULL
ALTER TABLE api_tokens
    ALTER COLUMN org_id SET NOT NULL;

-- Index for token lookups (hash lookup already exists, add org for validation)
CREATE INDEX IF NOT EXISTS idx_api_tokens_org_id ON api_tokens(org_id);

COMMENT ON COLUMN api_tokens.org_id IS 'Organization this token grants access to.';

-- ============================================================================
-- STEP 5: Add org_id Column to Services Table
-- ============================================================================
-- Services (product catalog) are organization-specific.

ALTER TABLE services
    ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

-- No existing services, so we can make it NOT NULL immediately
ALTER TABLE services
    ALTER COLUMN org_id SET NOT NULL;

-- Index for listing services by org
CREATE INDEX IF NOT EXISTS idx_services_org_id ON services(org_id);

-- Composite index: list public services in an org
CREATE INDEX IF NOT EXISTS idx_services_org_public ON services(org_id, public) WHERE deleted_at IS NULL;

COMMENT ON COLUMN services.org_id IS 'Organization that owns this service.';

-- ============================================================================
-- STEP 6: Add org_id Column to Orders Table
-- ============================================================================
-- Orders are the core transactional entity, always org-scoped.

ALTER TABLE orders
    ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

-- No existing orders, so we can make it NOT NULL immediately
ALTER TABLE orders
    ALTER COLUMN org_id SET NOT NULL;

-- Index for listing orders by org
CREATE INDEX IF NOT EXISTS idx_orders_org_id ON orders(org_id);

-- Composite index: list orders by org and status
CREATE INDEX IF NOT EXISTS idx_orders_org_status ON orders(org_id, status) WHERE deleted_at IS NULL;

-- Composite index: list orders by org and client
CREATE INDEX IF NOT EXISTS idx_orders_org_user ON orders(org_id, user_id) WHERE deleted_at IS NULL;

COMMENT ON COLUMN orders.org_id IS 'Organization this order belongs to.';

-- ============================================================================
-- STEP 7: Add org_id Column to Order Items Table (if exists)
-- ============================================================================
-- Order items inherit org from their parent order, but we add for query efficiency.

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'order_items') THEN
        ALTER TABLE order_items
            ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

        -- No existing order items
        ALTER TABLE order_items
            ALTER COLUMN org_id SET NOT NULL;

        CREATE INDEX IF NOT EXISTS idx_order_items_org_id ON order_items(org_id);
    END IF;
END $$;

-- ============================================================================
-- STEP 8: Add org_id Column to Order Tasks Table
-- ============================================================================
-- Tasks are org-scoped for efficient querying without joining orders.

ALTER TABLE order_tasks
    ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

-- No existing tasks
ALTER TABLE order_tasks
    ALTER COLUMN org_id SET NOT NULL;

-- Index for listing tasks by org
CREATE INDEX IF NOT EXISTS idx_order_tasks_org_id ON order_tasks(org_id);

COMMENT ON COLUMN order_tasks.org_id IS 'Organization this task belongs to (denormalized from order).';

-- ============================================================================
-- STEP 9: Add org_id Column to Order Messages Table
-- ============================================================================
-- Messages are org-scoped for efficient querying.

ALTER TABLE order_messages
    ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

-- No existing messages
ALTER TABLE order_messages
    ALTER COLUMN org_id SET NOT NULL;

-- Index for listing messages by org
CREATE INDEX IF NOT EXISTS idx_order_messages_org_id ON order_messages(org_id);

COMMENT ON COLUMN order_messages.org_id IS 'Organization this message belongs to (denormalized from order).';

-- ============================================================================
-- STEP 10: Add org_id Column to Invoices Table
-- ============================================================================
-- Invoices are financial records, always org-scoped.

ALTER TABLE invoices
    ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

-- No existing invoices
ALTER TABLE invoices
    ALTER COLUMN org_id SET NOT NULL;

-- Index for listing invoices by org
CREATE INDEX IF NOT EXISTS idx_invoices_org_id ON invoices(org_id);

-- Composite index: list invoices by org and status
CREATE INDEX IF NOT EXISTS idx_invoices_org_status ON invoices(org_id, status) WHERE deleted_at IS NULL;

COMMENT ON COLUMN invoices.org_id IS 'Organization this invoice belongs to.';

-- ============================================================================
-- STEP 11: Add org_id Column to Subscriptions Table (if exists)
-- ============================================================================
-- Subscriptions track recurring billing, org-scoped.

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'subscriptions') THEN
        ALTER TABLE subscriptions
            ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

        -- No existing subscriptions
        ALTER TABLE subscriptions
            ALTER COLUMN org_id SET NOT NULL;

        CREATE INDEX IF NOT EXISTS idx_subscriptions_org_id ON subscriptions(org_id);
    END IF;
END $$;

-- ============================================================================
-- STEP 12: Add org_id Column to Tickets Table (if exists)
-- ============================================================================
-- Support tickets are org-scoped.

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tickets') THEN
        ALTER TABLE tickets
            ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

        -- No existing tickets
        ALTER TABLE tickets
            ALTER COLUMN org_id SET NOT NULL;

        CREATE INDEX IF NOT EXISTS idx_tickets_org_id ON tickets(org_id);
    END IF;
END $$;

-- ============================================================================
-- STEP 13: Add org_id Column to Forms Table (if exists)
-- ============================================================================
-- Form definitions are org-specific.

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'forms') THEN
        ALTER TABLE forms
            ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

        ALTER TABLE forms
            ALTER COLUMN org_id SET NOT NULL;

        CREATE INDEX IF NOT EXISTS idx_forms_org_id ON forms(org_id);
    END IF;
END $$;

-- ============================================================================
-- STEP 14: Add org_id Column to Filled Forms Table (if exists)
-- ============================================================================
-- Submitted form data is org-scoped.

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'filled_forms') THEN
        ALTER TABLE filled_forms
            ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

        ALTER TABLE filled_forms
            ALTER COLUMN org_id SET NOT NULL;

        CREATE INDEX IF NOT EXISTS idx_filled_forms_org_id ON filled_forms(org_id);
    END IF;
END $$;

-- ============================================================================
-- STEP 15: Add org_id to Tags Table
-- ============================================================================
-- Tags should also be org-scoped (each org has their own tag taxonomy).

ALTER TABLE tags
    ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

-- Tags table is empty, so we can set NOT NULL immediately
-- But first check if there are any rows
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM tags) = 0 THEN
        ALTER TABLE tags ALTER COLUMN org_id SET NOT NULL;
    ELSE
        RAISE NOTICE 'Tags table has data - org_id left nullable. Assign orgs manually.';
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_tags_org_id ON tags(org_id);

COMMENT ON COLUMN tags.org_id IS 'Organization that owns this tag.';

-- ============================================================================
-- STEP 16: Add org_id to Addresses Table
-- ============================================================================
-- Addresses belong to clients, which belong to orgs.

ALTER TABLE addresses
    ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

-- Addresses table is empty
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM addresses) = 0 THEN
        ALTER TABLE addresses ALTER COLUMN org_id SET NOT NULL;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_addresses_org_id ON addresses(org_id);

COMMENT ON COLUMN addresses.org_id IS 'Organization this address belongs to.';

-- ============================================================================
-- STEP 17: Update Sessions Table (Optional - for audit trail)
-- ============================================================================
-- Sessions don't strictly need org_id since they reference user_id,
-- but adding it simplifies session cleanup per org.

ALTER TABLE sessions
    ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

-- Update existing sessions based on their user's org
UPDATE sessions s
SET org_id = u.org_id
FROM users u
WHERE s.user_id = u.id
AND s.org_id IS NULL;

-- Make org_id NOT NULL for future sessions
ALTER TABLE sessions
    ALTER COLUMN org_id SET NOT NULL;

CREATE INDEX IF NOT EXISTS idx_sessions_org_id ON sessions(org_id);

COMMENT ON COLUMN sessions.org_id IS 'Organization context for this session.';

-- ============================================================================
-- STEP 18: Create Helper Function for Current Org Context
-- ============================================================================
-- This function can be used in RLS policies if you enable row-level security.

CREATE OR REPLACE FUNCTION current_org_id()
RETURNS UUID
LANGUAGE sql
STABLE
AS $$
    SELECT NULLIF(current_setting('app.current_org_id', true), '')::UUID
$$;

COMMENT ON FUNCTION current_org_id IS 'Returns the current org context (set via SET app.current_org_id)';

-- ============================================================================
-- STEP 19: Verification Queries
-- ============================================================================
-- Run these after the migration to verify everything is correct.

DO $$
DECLARE
    org_count INTEGER;
    user_without_org INTEGER;
    token_without_org INTEGER;
BEGIN
    -- Count organizations
    SELECT COUNT(*) INTO org_count FROM organizations;
    RAISE NOTICE 'Organizations created: %', org_count;

    -- Check for users without org
    SELECT COUNT(*) INTO user_without_org FROM users WHERE org_id IS NULL;
    IF user_without_org > 0 THEN
        RAISE WARNING 'Users without org_id: %', user_without_org;
    ELSE
        RAISE NOTICE 'All users have org_id assigned ✓';
    END IF;

    -- Check for tokens without org
    SELECT COUNT(*) INTO token_without_org FROM api_tokens WHERE org_id IS NULL;
    IF token_without_org > 0 THEN
        RAISE WARNING 'API tokens without org_id: %', token_without_org;
    ELSE
        RAISE NOTICE 'All API tokens have org_id assigned ✓';
    END IF;
END $$;

-- ============================================================================
-- STEP 20: Summary Report
-- ============================================================================

SELECT 'MIGRATION COMPLETE' AS status;

SELECT
    o.name AS organization,
    o.slug,
    (SELECT COUNT(*) FROM users WHERE org_id = o.id) AS users,
    (SELECT COUNT(*) FROM api_tokens WHERE org_id = o.id) AS api_tokens,
    (SELECT COUNT(*) FROM sessions WHERE org_id = o.id) AS sessions
FROM organizations o
ORDER BY o.name;

COMMIT;

-- ============================================================================
-- POST-MIGRATION NOTES
-- ============================================================================
--
-- 1. UPDATE APPLICATION CODE:
--    - Modify validateApiToken() in lib/auth.ts to return orgId
--    - Add org_id to all INSERT statements
--    - Add org_id filtering to all SELECT queries
--    - Update OpenAPI specs to document org context
--
-- 2. AUTHENTICATION FLOW CHANGE:
--    Before: validateApiToken() returns { valid, userId }
--    After:  validateApiToken() returns { valid, userId, orgId }
--
-- 3. QUERY PATTERN CHANGE:
--    Before: supabase.from('services').select('*')
--    After:  supabase.from('services').select('*').eq('org_id', auth.orgId)
--
-- 4. CREATE OPERATIONS:
--    All INSERT statements must include org_id from the auth context.
--
-- 5. OPTIONAL - ENABLE ROW LEVEL SECURITY (RLS):
--    For additional security, enable RLS on tables and use policies like:
--
--    ALTER TABLE services ENABLE ROW LEVEL SECURITY;
--    CREATE POLICY "org_isolation" ON services
--        USING (org_id = current_org_id());
--
-- ============================================================================
