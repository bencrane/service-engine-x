-- Migration: Backfill Clients to Accounts/Contacts
-- Date: 2026-02-13
-- Description: Migrate existing clients (users with dashboard_access=0) to accounts + contacts
--
-- This migration should be run AFTER 006_add_accounts_contacts.sql
-- and AFTER the application code has been deployed with dual-write support.

-- ============================================================================
-- 1. CREATE ACCOUNTS FROM EXISTING CLIENTS
-- Group by company name, or create individual accounts for clients without company
-- ============================================================================

-- Insert accounts from clients that have a company name (group by company)
INSERT INTO accounts (
  id,
  org_id,
  name,
  lifecycle,
  balance,
  total_spent,
  stripe_customer_id,
  tax_id,
  aff_id,
  aff_link,
  ga_cid,
  billing_address_id,
  created_at,
  updated_at
)
SELECT DISTINCT ON (u.org_id, COALESCE(NULLIF(TRIM(u.company), ''), u.email))
  gen_random_uuid(),
  u.org_id,
  COALESCE(NULLIF(TRIM(u.company), ''), CONCAT(u.name_f, ' ', u.name_l)),
  CASE
    WHEN EXISTS (
      SELECT 1 FROM engagements e
      WHERE e.client_id = u.id AND e.status = 1
    ) THEN 'active'
    WHEN EXISTS (
      SELECT 1 FROM orders o
      WHERE o.user_id = u.id AND o.status IN (1, 2)
    ) THEN 'active'
    ELSE 'inactive'
  END,
  COALESCE(CAST(u.balance AS DECIMAL(12,2)), 0.00),
  COALESCE(CAST(u.spent AS DECIMAL(12,2)), 0.00),
  u.stripe_id,
  u.tax_id,
  u.aff_id,
  u.aff_link,
  u.ga_cid,
  u.address_id,
  u.created_at,
  NOW()
FROM users u
JOIN roles r ON u.role_id = r.id
WHERE r.dashboard_access = 0
ORDER BY u.org_id, COALESCE(NULLIF(TRIM(u.company), ''), u.email), u.created_at ASC;

-- ============================================================================
-- 2. CREATE CONTACTS FROM EXISTING CLIENTS
-- ============================================================================

-- Create a temporary mapping table to link users to accounts
CREATE TEMP TABLE user_account_map AS
SELECT
  u.id AS user_id,
  u.org_id,
  a.id AS account_id
FROM users u
JOIN roles r ON u.role_id = r.id
JOIN accounts a ON a.org_id = u.org_id
  AND a.name = COALESCE(NULLIF(TRIM(u.company), ''), CONCAT(u.name_f, ' ', u.name_l))
WHERE r.dashboard_access = 0;

-- Insert contacts for all clients
INSERT INTO contacts (
  id,
  org_id,
  account_id,
  name_f,
  name_l,
  email,
  phone,
  user_id,
  is_primary,
  is_billing,
  optin,
  created_at,
  updated_at
)
SELECT
  gen_random_uuid(),
  u.org_id,
  m.account_id,
  u.name_f,
  u.name_l,
  u.email,
  u.phone,
  u.id,  -- Link back to user for portal access
  TRUE,  -- First contact for account is primary
  TRUE,  -- First contact for account is billing
  u.optin,
  u.created_at,
  NOW()
FROM users u
JOIN roles r ON u.role_id = r.id
JOIN user_account_map m ON m.user_id = u.id
WHERE r.dashboard_access = 0
ON CONFLICT (org_id, email) WHERE deleted_at IS NULL DO NOTHING;

-- ============================================================================
-- 3. POPULATE account_id ON EXISTING ENGAGEMENTS
-- ============================================================================

UPDATE engagements e
SET account_id = m.account_id
FROM user_account_map m
WHERE e.client_id = m.user_id
  AND e.account_id IS NULL;

-- ============================================================================
-- 4. POPULATE account_id ON EXISTING ORDERS
-- ============================================================================

UPDATE orders o
SET account_id = m.account_id
FROM user_account_map m
WHERE o.user_id = m.user_id
  AND o.account_id IS NULL;

-- ============================================================================
-- 5. POPULATE account_id ON EXISTING INVOICES
-- ============================================================================

UPDATE invoices i
SET account_id = m.account_id
FROM user_account_map m
WHERE i.user_id = m.user_id
  AND i.account_id IS NULL;

-- ============================================================================
-- 6. POPULATE account_id ON EXISTING TICKETS
-- ============================================================================

UPDATE tickets t
SET account_id = m.account_id
FROM user_account_map m
WHERE t.user_id = m.user_id
  AND t.account_id IS NULL;

-- ============================================================================
-- 7. POPULATE account_id ON EXISTING PROPOSALS (based on email match)
-- ============================================================================

UPDATE proposals p
SET account_id = c.account_id
FROM contacts c
WHERE c.email = p.client_email
  AND c.org_id = p.org_id
  AND p.account_id IS NULL
  AND c.deleted_at IS NULL;

-- ============================================================================
-- 8. CLEANUP
-- ============================================================================

DROP TABLE user_account_map;

-- ============================================================================
-- VERIFICATION QUERIES (run manually to verify migration)
-- ============================================================================

-- Check account count matches approximate client count:
-- SELECT org_id, COUNT(*) FROM accounts GROUP BY org_id;
-- SELECT org_id, COUNT(*) FROM users u JOIN roles r ON u.role_id = r.id WHERE r.dashboard_access = 0 GROUP BY org_id;

-- Check all engagements have account_id:
-- SELECT COUNT(*) FROM engagements WHERE account_id IS NULL;

-- Check all orders from clients have account_id:
-- SELECT COUNT(*) FROM orders o JOIN users u ON o.user_id = u.id JOIN roles r ON u.role_id = r.id WHERE r.dashboard_access = 0 AND o.account_id IS NULL;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
