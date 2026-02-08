-- Migration: 003_proposal_items_project_centric.sql
-- Description: Make proposal items project-centric instead of service-centric
-- Date: 2026-02-08
--
-- Proposals sell projects, not services. Each proposal item defines a project
-- that will be created when the proposal is signed. The service_id is now an
-- optional internal reference for templating purposes.

-- ============================================
-- 1. ADD NAME AND DESCRIPTION TO PROPOSAL_ITEMS
-- ============================================

ALTER TABLE proposal_items
  ADD COLUMN name TEXT,
  ADD COLUMN description TEXT;

-- ============================================
-- 2. MIGRATE EXISTING DATA
-- ============================================
-- Populate name/description from linked services for existing items

UPDATE proposal_items pi
SET
  name = s.name,
  description = s.description
FROM services s
WHERE pi.service_id = s.id
  AND pi.name IS NULL;

-- ============================================
-- 3. MAKE NAME NOT NULL
-- ============================================
-- Now that data is migrated, enforce NOT NULL on name

ALTER TABLE proposal_items
  ALTER COLUMN name SET NOT NULL;

-- ============================================
-- 4. MAKE SERVICE_ID NULLABLE
-- ============================================
-- service_id is now optional (internal template reference)

ALTER TABLE proposal_items
  ALTER COLUMN service_id DROP NOT NULL;

-- ============================================
-- 5. UPDATE COMMENTS
-- ============================================

COMMENT ON TABLE proposal_items IS 'Project definitions on a proposal - each item becomes a project when signed';
COMMENT ON COLUMN proposal_items.name IS 'Project name (required)';
COMMENT ON COLUMN proposal_items.description IS 'Project scope/description';
COMMENT ON COLUMN proposal_items.service_id IS 'Optional reference to service template';

-- ============================================
-- 6. VERIFICATION
-- ============================================

DO $$
BEGIN
  -- Verify name column exists and is NOT NULL
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'proposal_items'
      AND column_name = 'name'
      AND is_nullable = 'NO'
  ) THEN
    RAISE EXCEPTION 'proposal_items.name column not created correctly';
  END IF;

  -- Verify service_id is now nullable
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'proposal_items'
      AND column_name = 'service_id'
      AND is_nullable = 'YES'
  ) THEN
    RAISE EXCEPTION 'proposal_items.service_id should be nullable';
  END IF;

  RAISE NOTICE 'Migration 003_proposal_items_project_centric completed successfully';
END $$;
