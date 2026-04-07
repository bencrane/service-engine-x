-- Migration: Add stripe_publishable_key to organizations
-- Date: 2026-04-07
-- Description: Store per-org Stripe publishable key so the frontend can
--   initialize Stripe.js with the correct key for each org.

ALTER TABLE organizations
  ADD COLUMN stripe_publishable_key VARCHAR(255);

COMMENT ON COLUMN organizations.stripe_publishable_key IS 'Stripe publishable key (pk_live_/pk_test_) for client-side Stripe.js initialization';
