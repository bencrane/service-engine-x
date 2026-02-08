# Proposal API Architecture Changes

**Date:** 2026-02-08
**Migration:** `003_proposal_items_project_centric.sql`

## Overview

The Proposals API has been refactored from a **service-centric** model to a **project-centric** model. Proposals now directly define the projects that will be created when signed, rather than referencing services from an internal catalog.

### Before: Service-Centric

```
Proposal Item → references Service → Project inherits service name/description
```

- Proposal items required a `service_id`
- Project name/description came from the linked service
- Clients saw internal service catalog names

### After: Project-Centric

```
Proposal Item (name, description, price) → becomes → Project
```

- Proposal items define project name and description directly
- `service_id` is optional (internal template reference only)
- Clients see exactly what was proposed

---

## Schema Changes

### Pydantic Models

#### ProposalItemInput (Request)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `str` | Yes | Project name |
| `description` | `str` | Yes | Project scope/description |
| `price` | `float` | Yes | Project price (>= 0) |
| `service_id` | `str \| None` | No | Optional service template reference |

**Removed:** `quantity` field (proposals sell projects, not units)

#### ProposalItemResponse

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Item UUID |
| `name` | `str` | Project name |
| `description` | `str \| None` | Project description |
| `price` | `str` | Project price |
| `service_id` | `str \| None` | Service template reference (if any) |
| `created_at` | `str` | ISO timestamp |

**Removed:** `service_name`, `service_description`, `quantity`

### Database Schema

```sql
-- proposal_items table changes
ALTER TABLE proposal_items
  ADD COLUMN name TEXT NOT NULL,
  ADD COLUMN description TEXT;

ALTER TABLE proposal_items
  ALTER COLUMN service_id DROP NOT NULL;
```

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `name` | `TEXT` | No | Project name (new) |
| `description` | `TEXT` | Yes | Project description (new) |
| `service_id` | `UUID` | Yes | Now optional |
| `quantity` | `INTEGER` | No | Retained for backwards compatibility |

---

## API Contract

### POST /api/proposals

Create a new proposal with project definitions.

**Request:**
```json
{
  "client_email": "client@example.com",
  "client_name_f": "John",
  "client_name_l": "Doe",
  "client_company": "Acme Corp",
  "items": [
    {
      "name": "Website Redesign",
      "description": "Complete redesign of company website including new branding, responsive layout, and CMS integration.",
      "price": 8500.00
    },
    {
      "name": "SEO Optimization",
      "description": "Technical SEO audit and implementation of recommendations.",
      "price": 2500.00,
      "service_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  ],
  "notes": "Q1 2026 project bundle"
}
```

**Response:**
```json
{
  "id": "proposal-uuid",
  "client_email": "client@example.com",
  "client_name": "John Doe",
  "client_name_f": "John",
  "client_name_l": "Doe",
  "client_company": "Acme Corp",
  "status": "Draft",
  "status_id": 0,
  "total": "11000.00",
  "notes": "Q1 2026 project bundle",
  "created_at": "2026-02-08T12:00:00Z",
  "updated_at": "2026-02-08T12:00:00Z",
  "sent_at": null,
  "signed_at": null,
  "converted_order_id": null,
  "converted_engagement_id": null,
  "items": [
    {
      "id": "item-uuid-1",
      "name": "Website Redesign",
      "description": "Complete redesign of company website...",
      "price": "8500.00",
      "service_id": null,
      "created_at": "2026-02-08T12:00:00Z"
    },
    {
      "id": "item-uuid-2",
      "name": "SEO Optimization",
      "description": "Technical SEO audit and implementation...",
      "price": "2500.00",
      "service_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2026-02-08T12:00:00Z"
    }
  ]
}
```

### Validation Rules

| Rule | Behavior |
|------|----------|
| `name` empty | 422 - name is required |
| `description` empty | 422 - description is required |
| `price` negative | 422 - price must be >= 0 |
| `service_id` invalid | 422 - service does not exist (only if provided) |
| `items` empty | 422 - at least one item required |

---

## Signing Flow

When a proposal is signed via `POST /api/proposals/{id}/sign`:

### Project Creation

Each proposal item becomes a project:

```
proposal_item.name        → project.name
proposal_item.description → project.description
proposal_item.service_id  → project.service_id (optional reference)
```

**Before (service-centric):**
```python
project_name = service.get("name") if service else f"Project {n}"
project_description = service.get("description") if service else None
```

**After (project-centric):**
```python
project_name = item["name"]
project_description = item.get("description")
```

### Order Metadata

The order created on signing stores proposal items in metadata:

```json
{
  "metadata": {
    "proposal_id": "...",
    "engagement_id": "...",
    "proposal_items": [
      {
        "name": "Website Redesign",
        "description": "Complete redesign...",
        "price": "8500.00",
        "service_id": null
      }
    ]
  }
}
```

---

## Migration Notes

### Backwards Compatibility

- Existing `proposal_items` with `service_id` had `name` and `description` populated from the linked service during migration
- The `quantity` column is retained but not used in new API responses
- `service_id` remains on projects for internal reference/templating

### Data Migration

```sql
UPDATE proposal_items pi
SET
  name = s.name,
  description = s.description
FROM services s
WHERE pi.service_id = s.id
  AND pi.name IS NULL;
```

---

## Rationale

1. **Client-facing clarity**: Proposals show exactly what the client is buying, not internal catalog references
2. **Flexibility**: Custom projects can be proposed without pre-creating services
3. **Decoupling**: Service catalog is internal tooling; proposals are external documents
4. **Sales pipeline fit**: Proposals define scope during sales, services are operational templates

The service catalog remains useful for:
- Populating proposal items from templates (via `service_id`)
- Standardizing pricing and scope
- Internal reporting and categorization
