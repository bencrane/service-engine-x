# Engagement Model: Database Schema Design

**Date:** 2026-02-08
**Status:** Approved

---

## 1. New Tables

### engagements

The work relationship container with a client.

```sql
CREATE TABLE engagements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id),
  client_id UUID NOT NULL REFERENCES users(id),

  name VARCHAR(255),                    -- Optional display name
  status INTEGER NOT NULL DEFAULT 1,    -- 1=Active, 2=Paused, 3=Closed

  proposal_id UUID REFERENCES proposals(id),  -- Originating proposal (if any)

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  closed_at TIMESTAMPTZ                 -- When status changed to Closed
);

CREATE INDEX idx_engagements_org_id ON engagements(org_id);
CREATE INDEX idx_engagements_client_id ON engagements(client_id);
CREATE INDEX idx_engagements_status ON engagements(status);
```

**Status values:**
| Value | Label | Description |
|-------|-------|-------------|
| 1 | Active | Work is ongoing |
| 2 | Paused | Temporarily on hold |
| 3 | Closed | Relationship ended |

---

### projects

Discrete deliverables within an engagement, progressing through phases.

```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
  org_id UUID NOT NULL REFERENCES organizations(id),

  name VARCHAR(255) NOT NULL,
  description TEXT,

  status INTEGER NOT NULL DEFAULT 1,    -- 1=Active, 2=Paused, 3=Completed, 4=Cancelled
  phase INTEGER NOT NULL DEFAULT 1,     -- 1=Kickoff, 2=Setup, 3=Build, 4=Testing, 5=Deployment, 6=Handoff

  service_id UUID REFERENCES services(id),  -- Template this project is based on (optional)

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ,             -- When status changed to Completed
  deleted_at TIMESTAMPTZ                -- Soft delete
);

CREATE INDEX idx_projects_engagement_id ON projects(engagement_id);
CREATE INDEX idx_projects_org_id ON projects(org_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_phase ON projects(phase);
```

**Status values:**
| Value | Label | Description |
|-------|-------|-------------|
| 1 | Active | Work in progress |
| 2 | Paused | Temporarily on hold |
| 3 | Completed | Deliverable finished |
| 4 | Cancelled | Work stopped, not completing |

**Phase values:**
| Value | Label | Description |
|-------|-------|-------------|
| 1 | Kickoff | Initial meeting, requirements gathering |
| 2 | Setup | Environment setup, access provisioning |
| 3 | Build | Active development/creation |
| 4 | Testing | QA, review cycles |
| 5 | Deployment | Launch, go-live |
| 6 | Handoff | Documentation, training, transition |

---

### conversations

Engagement-scoped communication threads.

```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
  org_id UUID NOT NULL REFERENCES organizations(id),

  subject VARCHAR(255),                 -- Topic/title of conversation
  status INTEGER NOT NULL DEFAULT 1,    -- 1=Open, 2=Closed

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_message_at TIMESTAMPTZ           -- For sorting by recent activity
);

CREATE INDEX idx_conversations_engagement_id ON conversations(engagement_id);
CREATE INDEX idx_conversations_org_id ON conversations(org_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_last_message_at ON conversations(last_message_at DESC);
```

**Status values:**
| Value | Label |
|-------|-------|
| 1 | Open |
| 2 | Closed |

---

### conversation_messages

Individual messages within a conversation.

```sql
CREATE TABLE conversation_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  org_id UUID NOT NULL REFERENCES organizations(id),

  sender_id UUID NOT NULL REFERENCES users(id),
  content TEXT NOT NULL,

  is_internal BOOLEAN NOT NULL DEFAULT FALSE,  -- Staff-only message (not visible to client)
  attachments JSONB DEFAULT '[]',              -- Array of {name, url, size}

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ                -- Soft delete
);

CREATE INDEX idx_conversation_messages_conversation_id ON conversation_messages(conversation_id);
CREATE INDEX idx_conversation_messages_org_id ON conversation_messages(org_id);
CREATE INDEX idx_conversation_messages_created_at ON conversation_messages(created_at);
```

---

## 2. Modifications to Existing Tables

### orders

Add engagement reference (which engagement this order funds).

```sql
ALTER TABLE orders
  ADD COLUMN engagement_id UUID REFERENCES engagements(id);

CREATE INDEX idx_orders_engagement_id ON orders(engagement_id);
```

---

### proposals

Add engagement reference (filled when proposal is signed).

```sql
ALTER TABLE proposals
  ADD COLUMN converted_engagement_id UUID REFERENCES engagements(id);
```

**Updated signing flow:**
- `converted_order_id` - the financial transaction
- `converted_engagement_id` - the work container

---

## 3. Entity Relationships

```
┌─────────────┐
│  proposals  │
└──────┬──────┘
       │ signs into
       ▼
┌─────────────┐     ┌─────────────┐
│   orders    │◄────│ engagements │
│ (financial) │     │   (work)    │
└─────────────┘     └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ projects │ │ projects │ │ conver-  │
        │          │ │          │ │ sations  │
        └──────────┘ └──────────┘ └────┬─────┘
                                       │
                                       ▼
                                 ┌──────────┐
                                 │ messages │
                                 └──────────┘
```

### Cardinality

| Relationship | Type |
|--------------|------|
| Client → Engagements | 1:many |
| Engagement → Projects | 1:many |
| Engagement → Conversations | 1:many |
| Engagement → Orders | 1:many (multiple orders can fund same engagement) |
| Conversation → Messages | 1:many |
| Proposal → Engagement | 1:1 (when signed) |
| Service → Projects | 1:many (template relationship) |

---

## 4. Multi-Tenancy

All tables include `org_id` for multi-tenant isolation:

- `engagements.org_id` - primary tenant key
- `projects.org_id` - denormalized from engagement for query efficiency
- `conversations.org_id` - denormalized from engagement
- `conversation_messages.org_id` - denormalized from conversation

All queries must filter by `org_id`.

---

## 5. Cascade Behavior

| Parent | Child | On Delete |
|--------|-------|-----------|
| engagements | projects | CASCADE |
| engagements | conversations | CASCADE |
| conversations | conversation_messages | CASCADE |
| engagements | orders | SET NULL (orders are financial records, keep them) |

---

## 6. Design Decisions

| Question | Decision |
|----------|----------|
| Employee assignments | Skip for now (solo operation). Add junction tables later if hiring. |
| Tags | Skip for now. Add later if needed for organization. |
| Files/attachments | JSONB array on messages: `attachments` with `{name, url, size}` objects. |
| Project ordering | Not needed. Display by phase/status, not manual order. |
| Conversation participants | Implicit. Engagement stakeholders (client + team) see all conversations. |
