-- Migration 011: Add organization bank details table
-- Stores bank account information per organization for wire/ACH payments
-- and display on invoices and proposals.

CREATE TABLE organization_bank_details (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,

  -- Account holder
  account_name VARCHAR(255) NOT NULL,

  -- Account identifiers
  account_number VARCHAR(34),          -- up to 34 chars (covers IBAN)
  routing_number VARCHAR(9),           -- ABA routing (US domestic)

  -- Bank info
  bank_name VARCHAR(255),
  bank_address_line1 VARCHAR(255),
  bank_address_line2 VARCHAR(255),
  bank_city VARCHAR(100),
  bank_state VARCHAR(100),
  bank_postal_code VARCHAR(20),
  bank_country VARCHAR(2),             -- ISO 3166-1 alpha-2

  -- International
  swift_code VARCHAR(11),              -- 8 or 11 characters
  iban VARCHAR(34),

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- One bank detail record per org
CREATE UNIQUE INDEX idx_org_bank_details_org_id ON organization_bank_details(org_id);
