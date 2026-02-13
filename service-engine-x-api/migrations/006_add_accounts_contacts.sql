-- Migration: Add Account/Contact Model
-- Date: 2026-02-13
-- Description: Implements Salesforce-style Account/Contact model to separate CRM data from auth data
--
-- Account = company (Greenfield Partners) with lifecycle status
-- Contact = person at account (Sarah Chen), optionally linked to a User for portal access
-- User = people who can log in (team members + contacts with portal access)

-- ============================================================================
-- 1. ACCOUNTS
-- Companies/organizations that are clients or leads
-- ============================================================================

CREATE TABLE accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id),

  name VARCHAR(255) NOT NULL,              -- Company name
  domain VARCHAR(255),                     -- Website domain
  lifecycle VARCHAR(20) NOT NULL DEFAULT 'lead',  -- lead, active, inactive, churned

  -- Financial (from users)
  balance DECIMAL(12,2) DEFAULT 0.00,
  total_spent DECIMAL(12,2) DEFAULT 0.00,
  stripe_customer_id VARCHAR(255),
  tax_id VARCHAR(50),

  -- Affiliate (from users)
  aff_id INTEGER,
  aff_link VARCHAR(255),

  -- Tracking
  source VARCHAR(50),
  ga_cid VARCHAR(100),
  custom_fields JSONB DEFAULT '{}',
  note TEXT,
  billing_address_id UUID REFERENCES addresses(id),

  -- Timestamps
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_accounts_org_id ON accounts(org_id);
CREATE INDEX idx_accounts_lifecycle ON accounts(lifecycle);
CREATE INDEX idx_accounts_domain ON accounts(domain);
CREATE INDEX idx_accounts_stripe_customer_id ON accounts(stripe_customer_id);
CREATE INDEX idx_accounts_deleted_at ON accounts(deleted_at) WHERE deleted_at IS NULL;

COMMENT ON TABLE accounts IS 'Companies/organizations that are clients or leads';
COMMENT ON COLUMN accounts.lifecycle IS 'lead, active, inactive, churned';
COMMENT ON COLUMN accounts.stripe_customer_id IS 'Stripe customer ID for billing';

-- ============================================================================
-- 2. CONTACTS
-- People at accounts, optionally linked to users for portal access
-- ============================================================================

CREATE TABLE contacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id),
  account_id UUID REFERENCES accounts(id),

  -- Identity
  name_f VARCHAR(100) NOT NULL,
  name_l VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL,
  phone VARCHAR(50),
  title VARCHAR(100),

  -- Portal access
  user_id UUID REFERENCES users(id),       -- If they can log in

  -- Role flags
  is_primary BOOLEAN DEFAULT FALSE,
  is_billing BOOLEAN DEFAULT FALSE,
  optin VARCHAR(20),
  custom_fields JSONB DEFAULT '{}',

  -- Timestamps
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);

-- Unique constraint: one email per org (for non-deleted contacts)
CREATE UNIQUE INDEX idx_contacts_org_email_unique
  ON contacts(org_id, email)
  WHERE deleted_at IS NULL;

CREATE INDEX idx_contacts_org_id ON contacts(org_id);
CREATE INDEX idx_contacts_account_id ON contacts(account_id);
CREATE INDEX idx_contacts_user_id ON contacts(user_id);
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_deleted_at ON contacts(deleted_at) WHERE deleted_at IS NULL;

COMMENT ON TABLE contacts IS 'People at accounts, optionally linked to users for portal access';
COMMENT ON COLUMN contacts.user_id IS 'Link to user if contact has portal access';
COMMENT ON COLUMN contacts.is_primary IS 'Primary contact for the account';
COMMENT ON COLUMN contacts.is_billing IS 'Billing contact for the account';

-- ============================================================================
-- 3. ADD account_id TO EXISTING TABLES (NULLABLE FOR TRANSITION)
-- ============================================================================

-- Engagements: replaces client_id over time
ALTER TABLE engagements
  ADD COLUMN account_id UUID REFERENCES accounts(id);

CREATE INDEX idx_engagements_account_id ON engagements(account_id);
COMMENT ON COLUMN engagements.account_id IS 'Account for this engagement (replaces client_id)';

-- Orders: alongside user_id for tracking
ALTER TABLE orders
  ADD COLUMN account_id UUID REFERENCES accounts(id);

CREATE INDEX idx_orders_account_id ON orders(account_id);
COMMENT ON COLUMN orders.account_id IS 'Account for this order';

-- Invoices: alongside user_id for tracking
ALTER TABLE invoices
  ADD COLUMN account_id UUID REFERENCES accounts(id);

CREATE INDEX idx_invoices_account_id ON invoices(account_id);
COMMENT ON COLUMN invoices.account_id IS 'Account for this invoice';

-- Tickets: alongside user_id for tracking
ALTER TABLE tickets
  ADD COLUMN account_id UUID REFERENCES accounts(id);

CREATE INDEX idx_tickets_account_id ON tickets(account_id);
COMMENT ON COLUMN tickets.account_id IS 'Account for this ticket';

-- Proposals: for lead tracking
ALTER TABLE proposals
  ADD COLUMN account_id UUID REFERENCES accounts(id);

CREATE INDEX idx_proposals_account_id ON proposals(account_id);
COMMENT ON COLUMN proposals.account_id IS 'Account for this proposal (for lead tracking)';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
