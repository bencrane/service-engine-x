-- Migration 010: Add proposal_signatures table
-- Stores forensic signing data separately from the proposals table.
-- One signature per proposal (unique constraint on proposal_id).

CREATE TABLE proposal_signatures (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  proposal_id UUID NOT NULL REFERENCES proposals(id) ON DELETE CASCADE,
  org_id UUID NOT NULL REFERENCES organizations(id),

  -- Signer identity
  signer_name VARCHAR(255),
  signer_email VARCHAR(255),
  signature_data TEXT NOT NULL,          -- base64 PNG from signature pad

  -- Forensic metadata
  signer_ip VARCHAR(45),                -- IPv4 or IPv6
  signer_user_agent TEXT,
  client_signed_at TIMESTAMPTZ,         -- timestamp from the browser
  server_signed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Signed PDF
  signed_pdf_url TEXT,
  signed_pdf_hash VARCHAR(64),          -- SHA-256 hex digest of PDF bytes

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- One signature per proposal
CREATE UNIQUE INDEX idx_proposal_signatures_proposal_id ON proposal_signatures(proposal_id);
CREATE INDEX idx_proposal_signatures_org_id ON proposal_signatures(org_id);
