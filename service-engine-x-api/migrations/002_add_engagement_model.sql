-- Migration: Add Engagement Model
-- Date: 2026-02-08
-- Description: Creates tables for engagement-based project delivery model
--
-- New tables: engagements, projects, conversations, conversation_messages
-- Modified tables: orders (add engagement_id), proposals (add converted_engagement_id)

-- ============================================================================
-- 1. ENGAGEMENTS
-- The work relationship container with a client
-- ============================================================================

CREATE TABLE engagements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id),
  client_id UUID NOT NULL REFERENCES users(id),

  name VARCHAR(255),                              -- Optional display name
  status INTEGER NOT NULL DEFAULT 1,              -- 1=Active, 2=Paused, 3=Closed

  proposal_id UUID REFERENCES proposals(id),      -- Originating proposal (if any)

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  closed_at TIMESTAMPTZ                           -- When status changed to Closed
);

CREATE INDEX idx_engagements_org_id ON engagements(org_id);
CREATE INDEX idx_engagements_client_id ON engagements(client_id);
CREATE INDEX idx_engagements_status ON engagements(status);

COMMENT ON TABLE engagements IS 'Work relationship containers with clients';
COMMENT ON COLUMN engagements.status IS '1=Active, 2=Paused, 3=Closed';

-- ============================================================================
-- 2. PROJECTS
-- Discrete deliverables within an engagement, progressing through phases
-- ============================================================================

CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
  org_id UUID NOT NULL REFERENCES organizations(id),

  name VARCHAR(255) NOT NULL,
  description TEXT,

  status INTEGER NOT NULL DEFAULT 1,              -- 1=Active, 2=Paused, 3=Completed, 4=Cancelled
  phase INTEGER NOT NULL DEFAULT 1,               -- 1=Kickoff, 2=Setup, 3=Build, 4=Testing, 5=Deployment, 6=Handoff

  service_id UUID REFERENCES services(id),        -- Template this project is based on (optional)

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ,                       -- When status changed to Completed
  deleted_at TIMESTAMPTZ                          -- Soft delete
);

CREATE INDEX idx_projects_engagement_id ON projects(engagement_id);
CREATE INDEX idx_projects_org_id ON projects(org_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_phase ON projects(phase);
CREATE INDEX idx_projects_deleted_at ON projects(deleted_at) WHERE deleted_at IS NULL;

COMMENT ON TABLE projects IS 'Discrete deliverables within engagements';
COMMENT ON COLUMN projects.status IS '1=Active, 2=Paused, 3=Completed, 4=Cancelled';
COMMENT ON COLUMN projects.phase IS '1=Kickoff, 2=Setup, 3=Build, 4=Testing, 5=Deployment, 6=Handoff';

-- ============================================================================
-- 3. CONVERSATIONS
-- Engagement-scoped communication threads
-- ============================================================================

CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
  org_id UUID NOT NULL REFERENCES organizations(id),

  subject VARCHAR(255),                           -- Topic/title of conversation
  status INTEGER NOT NULL DEFAULT 1,              -- 1=Open, 2=Closed

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_message_at TIMESTAMPTZ                     -- For sorting by recent activity
);

CREATE INDEX idx_conversations_engagement_id ON conversations(engagement_id);
CREATE INDEX idx_conversations_org_id ON conversations(org_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_last_message_at ON conversations(last_message_at DESC NULLS LAST);

COMMENT ON TABLE conversations IS 'Engagement-scoped communication threads';
COMMENT ON COLUMN conversations.status IS '1=Open, 2=Closed';

-- ============================================================================
-- 4. CONVERSATION_MESSAGES
-- Individual messages within a conversation
-- ============================================================================

CREATE TABLE conversation_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  org_id UUID NOT NULL REFERENCES organizations(id),

  sender_id UUID NOT NULL REFERENCES users(id),
  content TEXT NOT NULL,

  is_internal BOOLEAN NOT NULL DEFAULT FALSE,     -- Staff-only message (not visible to client)
  attachments JSONB DEFAULT '[]',                 -- Array of {name, url, size}

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ                          -- Soft delete
);

CREATE INDEX idx_conversation_messages_conversation_id ON conversation_messages(conversation_id);
CREATE INDEX idx_conversation_messages_org_id ON conversation_messages(org_id);
CREATE INDEX idx_conversation_messages_created_at ON conversation_messages(created_at);
CREATE INDEX idx_conversation_messages_deleted_at ON conversation_messages(deleted_at) WHERE deleted_at IS NULL;

COMMENT ON TABLE conversation_messages IS 'Individual messages within conversations';
COMMENT ON COLUMN conversation_messages.is_internal IS 'Staff-only message not visible to client';
COMMENT ON COLUMN conversation_messages.attachments IS 'JSON array of {name, url, size} objects';

-- ============================================================================
-- 5. MODIFY ORDERS TABLE
-- Add engagement reference (which engagement this order funds)
-- ============================================================================

ALTER TABLE orders
  ADD COLUMN engagement_id UUID REFERENCES engagements(id);

CREATE INDEX idx_orders_engagement_id ON orders(engagement_id);

COMMENT ON COLUMN orders.engagement_id IS 'The engagement this order funds (if any)';

-- ============================================================================
-- 6. MODIFY PROPOSALS TABLE
-- Add engagement reference (filled when proposal is signed)
-- ============================================================================

ALTER TABLE proposals
  ADD COLUMN converted_engagement_id UUID REFERENCES engagements(id);

COMMENT ON COLUMN proposals.converted_engagement_id IS 'Engagement created when proposal was signed';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
