-- Migration: Add Stripe checkout fields for payment integration
-- Date: 2026-02-11
-- Description: Add fields to support Stripe Checkout after proposal signing
--
-- Rationale: When a proposal is signed, we create a Stripe Checkout session
-- with itemized line items. The checkout_url is returned to the frontend for
-- redirect. Webhook updates order status when payment completes.

-- ============================================================================
-- 1. ADD domain COLUMN TO organizations
-- ============================================================================

ALTER TABLE organizations
  ADD COLUMN domain VARCHAR(255);

COMMENT ON COLUMN organizations.domain IS 'Organization domain for Stripe success/cancel redirect URLs';

-- ============================================================================
-- 2. ADD stripe_webhook_secret COLUMN TO organizations
-- ============================================================================

ALTER TABLE organizations
  ADD COLUMN stripe_webhook_secret VARCHAR(255);

COMMENT ON COLUMN organizations.stripe_webhook_secret IS 'Stripe webhook signing secret for verifying webhook events';

-- ============================================================================
-- 3. ADD STRIPE FIELDS TO orders
-- ============================================================================

ALTER TABLE orders
  ADD COLUMN stripe_checkout_session_id VARCHAR(255),
  ADD COLUMN stripe_payment_intent_id VARCHAR(255),
  ADD COLUMN paid_at TIMESTAMPTZ;

COMMENT ON COLUMN orders.stripe_checkout_session_id IS 'Stripe Checkout Session ID for tracking payment';
COMMENT ON COLUMN orders.stripe_payment_intent_id IS 'Stripe PaymentIntent ID after successful payment';
COMMENT ON COLUMN orders.paid_at IS 'Timestamp when payment was completed';

-- ============================================================================
-- 4. ADD INDEXES
-- ============================================================================

CREATE INDEX idx_orders_stripe_checkout_session_id ON orders(stripe_checkout_session_id);

-- ============================================================================
-- 5. SEED DOMAIN VALUES FOR EXISTING ORGANIZATIONS
-- ============================================================================

-- Update domains based on organization names
UPDATE organizations SET domain = 'revenueactivation.com' WHERE name = 'Revenue Activation';
UPDATE organizations SET domain = 'everythingautomation.com' WHERE name = 'Everything Automation';
UPDATE organizations SET domain = 'outboundsolutions.com' WHERE name = 'Outbound Solutions';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
