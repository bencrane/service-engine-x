-- Migration: Add notification_email to organizations
-- Date: 2026-02-12
-- Description: Add email notification settings for proposal signing

-- ============================================================================
-- 1. ADD notification_email COLUMN TO organizations
-- ============================================================================

ALTER TABLE organizations
  ADD COLUMN IF NOT EXISTS notification_email VARCHAR(255);

COMMENT ON COLUMN organizations.notification_email IS 'Email address to receive proposal signed notifications';

-- ============================================================================
-- 2. SEED MODERN FULL ORG VALUES
-- ============================================================================

UPDATE organizations
SET
  domain = 'modernfull.com',
  notification_email = 'ben@modernfull.com'
WHERE name = 'Modern Full';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
