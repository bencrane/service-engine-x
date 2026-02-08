# Phase 7 Complete: Engagement-Based Model

**Date:** 2026-02-08
**Status:** Complete

## Summary

Phase 7 transformed Service-Engine-X from a transactional order-tracking system to an engagement-based project delivery platform. This is a fundamental reconceptualization of how the system models work relationships.

## Conceptual Shift

### Before (Order-Centric)
- Orders = transactions that also contained work delivery
- Communication fragmented between order_messages and tickets
- Client relationship implicit (just a collection of orders)

### After (Engagement-Centric)
- Engagements = work relationship containers
- Projects = discrete deliverables with phases
- Conversations = unified communication at engagement level
- Orders = financial transaction records only

## What Was Built

### 7a: Database Migration

**File:** `migrations/002_add_engagement_model.sql`

**New Tables:**
| Table | Purpose |
|-------|---------|
| `engagements` | Work relationship containers |
| `projects` | Discrete deliverables with phases |
| `conversations` | Engagement-scoped communication |
| `conversation_messages` | Messages within conversations |

**Modified Tables:**
| Table | Change |
|-------|--------|
| `orders` | Added `engagement_id` column |
| `proposals` | Added `converted_engagement_id` column |

### 7b: Engagements API

**Endpoints (5):**
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/engagements` | List with pagination |
| POST | `/api/engagements` | Create engagement |
| GET | `/api/engagements/{id}` | Retrieve with projects & conversations |
| PUT | `/api/engagements/{id}` | Update engagement |
| DELETE | `/api/engagements/{id}` | Close engagement |

**Status System:**
- 1 = Active
- 2 = Paused
- 3 = Closed

### 7c: Projects API

**Endpoints (6):**
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/projects` | List with filters |
| POST | `/api/projects` | Create project |
| GET | `/api/projects/{id}` | Retrieve project |
| PUT | `/api/projects/{id}` | Update project |
| DELETE | `/api/projects/{id}` | Soft delete |
| POST | `/api/projects/{id}/advance` | Advance to next phase |

**Phase System:**
```
1. Kickoff → 2. Setup → 3. Build → 4. Testing → 5. Deployment → 6. Handoff
                                        ↓
                                      Build (can return for fixes)
```

**Status System:**
- 1 = Active
- 2 = Paused
- 3 = Completed
- 4 = Cancelled

### 7d: Conversations API

**Endpoints (8):**
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/conversations` | List conversations |
| POST | `/api/conversations` | Create conversation |
| GET | `/api/conversations/{id}` | Retrieve with messages |
| PUT | `/api/conversations/{id}` | Update conversation |
| DELETE | `/api/conversations/{id}` | Close conversation |
| GET | `/api/conversations/{id}/messages` | List messages |
| POST | `/api/conversations/{id}/messages` | Create message |
| DELETE | `/api/conversations/{id}/messages/{msg_id}` | Delete message |

**Key Features:**
- `is_internal` flag for staff-only messages
- `attachments` JSONB array with `{name, url, size}`
- Automatic `last_message_at` updates

### 7e: Proposal Sign Flow

**Updated endpoint:** `POST /api/proposals/{id}/sign`

When a proposal is signed, now creates:
1. **Engagement** - Work relationship container
2. **Projects** - One per proposal item, starting at Kickoff phase
3. **Order** - Financial transaction record (linked to engagement)

**Response now includes:**
```json
{
  "proposal": {...},
  "engagement": {
    "id": "uuid",
    "name": "Client Name - Engagement",
    "status": "Active"
  },
  "projects": [
    {"id": "uuid", "name": "Service Name", "phase": "Kickoff"},
    {"id": "uuid", "name": "Service 2", "phase": "Kickoff"}
  ],
  "order": {..., "engagement_id": "uuid"}
}
```

## Files Created

### Models
- `app/models/engagements.py`
- `app/models/projects.py`
- `app/models/conversations.py`

### Routers
- `app/routers/engagements.py`
- `app/routers/projects.py`
- `app/routers/conversations.py`

### Tests
- `tests/test_engagements.py` (5 tests)
- `tests/test_projects.py` (6 tests)
- `tests/test_conversations.py` (8 tests)

### Documentation
- `ENGAGEMENT-MODEL.md` - Conceptual foundation
- `ENGAGEMENT-SCHEMA.md` - Database schema design
- `migrations/002_add_engagement_model.sql`

## Files Modified

- `app/models/proposals.py` - Added `converted_engagement_id`
- `app/routers/proposals.py` - Updated sign flow
- `app/models/__init__.py` - Added exports
- `app/routers/__init__.py` - Added routers
- `app/main.py` - Registered new routers

## API Summary

| Resource | Endpoints | Status |
|----------|-----------|--------|
| Engagements | 5 | Complete |
| Projects | 6 | Complete |
| Conversations | 8 | Complete |
| Proposals (updated) | 1 modified | Complete |
| **Total New** | **19** | |

## Entity Relationships

```
Proposal (signed)
    │
    ├──► Engagement (work container)
    │        │
    │        ├──► Project 1 (phase: Kickoff)
    │        ├──► Project 2 (phase: Kickoff)
    │        ├──► Conversation 1
    │        └──► Conversation 2
    │                  └──► Messages
    │
    └──► Order (financial record)
              └── engagement_id ──► links back
```

## 7f: Conversations Refactor (Project-Scoped)

**Migration:** `migrations/003_conversations_project_scoped.sql`

### Change Summary

Conversations were refactored from engagement-scoped to project-scoped:
- Conversations now belong to projects, not engagements
- Each project can have its own conversation threads
- Conversations are accessed via `/api/projects/{project_id}/conversations`

### Rationale

Clients see projects, not engagements. A client with "CRM Cleanup" and "Dashboard Build" projects should have separate conversation threads for each project.

### Updated Endpoints

| Method | Old Path | New Path |
|--------|----------|----------|
| GET | `/api/conversations` | `/api/projects/{project_id}/conversations` |
| POST | `/api/conversations` | `/api/projects/{project_id}/conversations` |
| GET | `/api/conversations/{id}` | `/api/projects/{project_id}/conversations/{id}` |
| PUT | `/api/conversations/{id}` | `/api/projects/{project_id}/conversations/{id}` |
| DELETE | `/api/conversations/{id}` | `/api/projects/{project_id}/conversations/{id}` |
| GET | `/api/conversations/{id}/messages` | `/api/projects/{project_id}/conversations/{id}/messages` |
| POST | `/api/conversations/{id}/messages` | `/api/projects/{project_id}/conversations/{id}/messages` |
| DELETE | `/api/conversations/{id}/messages/{msg_id}` | `/api/projects/{project_id}/conversations/{id}/messages/{msg_id}` |

### Database Changes

```sql
-- Added project_id, removed engagement_id
ALTER TABLE conversations ADD COLUMN project_id UUID REFERENCES projects(id);
ALTER TABLE conversations DROP COLUMN engagement_id;
CREATE INDEX idx_conversations_project_id ON conversations(project_id);
```

### Response Schema Changes

- `engagement_id` → `project_id`
- `engagement` → `project` (brief object)
- `EngagementBrief` → `ProjectBrief`

### Engagement Response Update

Engagements still include a `conversations` array in their response, but it now aggregates conversations from all projects within the engagement.

## Deprecation Path

The following tables are now superseded but not yet removed:
- `tickets` → replaced by `conversations`
- `ticket_messages` → replaced by `conversation_messages`
- `order_messages` → replaced by `conversation_messages`

These will be deprecated in a future phase after data migration.
