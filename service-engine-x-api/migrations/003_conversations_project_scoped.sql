-- Migration: Move conversations from engagement-scoped to project-scoped
-- Date: 2026-02-08
-- Description: Conversations should be tied to specific projects (deliverables), not engagements
--
-- Rationale: Clients see projects, not engagements. A client with "CRM Cleanup" and
-- "Dashboard Build" projects should have separate conversation threads for each.

-- ============================================================================
-- 1. ADD project_id COLUMN TO conversations
-- ============================================================================

ALTER TABLE conversations
  ADD COLUMN project_id UUID REFERENCES projects(id) ON DELETE CASCADE;

-- ============================================================================
-- 2. DROP engagement_id COLUMN (after adding project_id)
-- ============================================================================

-- First drop the index
DROP INDEX IF EXISTS idx_conversations_engagement_id;

-- Then drop the foreign key constraint and column
ALTER TABLE conversations
  DROP COLUMN engagement_id;

-- ============================================================================
-- 3. ADD INDEX FOR project_id
-- ============================================================================

CREATE INDEX idx_conversations_project_id ON conversations(project_id);

-- ============================================================================
-- 4. UPDATE COMMENTS
-- ============================================================================

COMMENT ON TABLE conversations IS 'Project-scoped communication threads';
COMMENT ON COLUMN conversations.project_id IS 'The project this conversation belongs to';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
