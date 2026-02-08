-- Migration: 004_add_documenso_to_proposals.sql
-- Description: Add Documenso e-signature fields to proposals
-- Date: 2026-02-08

-- ============================================
-- 1. ADD DOCUMENSO COLUMNS TO PROPOSALS
-- ============================================

ALTER TABLE proposals
  ADD COLUMN documenso_document_id TEXT,
  ADD COLUMN documenso_signing_token TEXT;

-- ============================================
-- 2. ADD COMMENTS
-- ============================================

COMMENT ON COLUMN proposals.documenso_document_id IS 'Documenso document ID for e-signature';
COMMENT ON COLUMN proposals.documenso_signing_token IS 'Token for embedding Documenso signing widget';

-- ============================================
-- 3. VERIFICATION
-- ============================================

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'proposals'
      AND column_name = 'documenso_signing_token'
  ) THEN
    RAISE EXCEPTION 'proposals.documenso_signing_token column not created';
  END IF;

  RAISE NOTICE 'Migration 004_add_documenso_to_proposals completed successfully';
END $$;
