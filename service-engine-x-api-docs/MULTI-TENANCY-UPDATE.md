# Multi-Tenancy Implementation Update

## Overview

This document details the comprehensive multi-tenancy implementation added to Service-Engine-X. The system now supports complete data isolation between organizations, ensuring that each tenant can only access their own data through the API.

## Database Migration

**Migration File:** `migrations/001_add_multi_tenant_support.sql`

### Organizations Table

A new `organizations` table was created to serve as the root tenant entity:

```sql
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(100) NOT NULL UNIQUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Seeded Organizations

Two organizations were seeded for initial use:

| Organization | UUID | Slug |
|-------------|------|------|
| Revenue Activation | `11111111-1111-1111-1111-111111111111` | `revenue-activation` |
| Outbound Solutions | `22222222-2222-2222-2222-222222222222` | `outbound-solutions` |

### Tables with org_id Column

The `org_id` column (UUID, NOT NULL, foreign key to organizations) was added to:

| Table | Purpose |
|-------|---------|
| `users` | Client and employee accounts |
| `services` | Service catalog items |
| `orders` | Customer orders |
| `invoices` | Billing invoices |
| `invoice_items` | Line items on invoices |
| `subscriptions` | Recurring billing subscriptions |
| `api_tokens` | API authentication tokens |
| `addresses` | User addresses |
| `order_items` | Order line items |
| `order_tasks` | Tasks assigned to orders |
| `order_messages` | Messages on orders |
| `forms` | Custom forms |
| `filled_forms` | Submitted form data |

### Data Assignment

Existing data was assigned to organizations based on user email domains:
- Users with `@revenueactivation.com` emails → Revenue Activation org
- Users with `@outboundsolutions.com` emails → Outbound Solutions org
- All other users → Revenue Activation org (default)

Related records (orders, invoices, services, etc.) were assigned based on their associated user's organization.

---

## Authentication Changes

### File: `lib/auth.ts`

#### Updated ApiAuthResult Interface

```typescript
export interface ApiAuthResult {
  valid: boolean;
  userId: string | null;
  orgId: string | null;  // NEW: Organization ID from API token
  error?: string;
}
```

#### Updated validateApiToken Function

The function now returns `orgId` from the API token record:

```typescript
export async function validateApiToken(token: string): Promise<ApiAuthResult> {
  const tokenHash = await hashToken(token);

  const { data: tokenRecord, error } = await supabase
    .from("api_tokens")
    .select("id, user_id, org_id, expires_at")  // Now includes org_id
    .eq("token_hash", tokenHash)
    .single();

  // ... validation logic ...

  return {
    valid: true,
    userId: tokenRecord.user_id,
    orgId: tokenRecord.org_id  // Returned to route handlers
  };
}
```

#### Updated createSession Function

Session creation now requires `orgId`:

```typescript
export async function createSession(userId: string, orgId: string): Promise<string>
```

---

## API Endpoint Updates

All API endpoints now enforce multi-tenant isolation. Each route:
1. Extracts the Bearer token from the Authorization header
2. Validates the token and retrieves the associated `orgId`
3. Passes `orgId` to implementation functions
4. Filters all database queries by `org_id`

### Authentication Pattern

Every route now follows this pattern:

```typescript
import { validateApiToken, extractBearerToken } from "@/lib/auth";

export async function GET(request: NextRequest) {
  const token = extractBearerToken(request.headers.get("authorization"));
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const auth = await validateApiToken(token);
  if (!auth.valid || !auth.orgId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  return listResource(request, auth.orgId);
}
```

---

## Clients API

### Files Updated

| File | Changes |
|------|---------|
| `app/api/clients/route.ts` | Added authentication, passes `orgId` to handlers |
| `app/api/clients/[id]/route.ts` | Added authentication, passes `orgId` to handlers |
| `app/api/clients/list-clients.ts` | Added `orgId` parameter, filters by `org_id` |
| `app/api/clients/create-client.ts` | Added `orgId` parameter, sets `org_id` on insert |
| `app/api/clients/[id]/retrieve-client.ts` | Added `orgId` parameter, filters by `org_id` |
| `app/api/clients/[id]/update-client.ts` | Added `orgId` parameter, filters by `org_id` |
| `app/api/clients/[id]/delete-client.ts` | Added `orgId` parameter, filters by `org_id` |

### Query Pattern

```typescript
// List query with org_id filter
let query = supabase
  .from("users")
  .select(`...`, { count: "exact" })
  .eq("org_id", orgId)
  .eq("role_id", clientRole.id);

// Create with org_id
const { data: newClient } = await supabase
  .from("users")
  .insert({
    org_id: orgId,
    email: input.email,
    // ... other fields
  });
```

---

## Services API

### Files Updated

| File | Changes |
|------|---------|
| `app/api/services/route.ts` | Added authentication (was previously unauthenticated!) |
| `app/api/services/[id]/route.ts` | Added authentication |
| `app/api/services/list-services.ts` | Added `orgId` parameter, filters by `org_id` |
| `app/api/services/create-service.ts` | Added `orgId` parameter, sets `org_id` on insert |
| `app/api/services/[id]/retrieve-service.ts` | Added `orgId` parameter, filters by `org_id` |
| `app/api/services/[id]/update-service.ts` | Added `orgId` parameter, filters by `org_id` |
| `app/api/services/[id]/delete-service.ts` | Added `orgId` parameter, filters by `org_id` |

---

## Invoices API

### Files Updated

| File | Changes |
|------|---------|
| `app/api/invoices/route.ts` | Added authentication |
| `app/api/invoices/[id]/route.ts` | Added authentication |
| `app/api/invoices/[id]/charge/route.ts` | Added authentication |
| `app/api/invoices/[id]/mark_paid/route.ts` | Added authentication |
| `app/api/invoices/list-invoices.ts` | Added `orgId` parameter, filters by `org_id` |
| `app/api/invoices/create-invoice.ts` | Added `orgId` parameter, sets `org_id` on insert |
| `app/api/invoices/[id]/retrieve-invoice.ts` | Added `orgId` parameter, filters by `org_id` |
| `app/api/invoices/[id]/update-invoice.ts` | Added `orgId` parameter, filters by `org_id` |
| `app/api/invoices/[id]/delete-invoice.ts` | Added `orgId` parameter, filters by `org_id` |
| `app/api/invoices/[id]/charge/charge-invoice.ts` | Added `orgId` parameter, filters by `org_id`, sets `org_id` on order creation |
| `app/api/invoices/[id]/mark_paid/mark-invoice-paid.ts` | Added `orgId` parameter, filters by `org_id`, sets `org_id` on order and subscription creation |

### Side Effects with org_id

When charging or marking an invoice as paid, related records are created with the correct `org_id`:

```typescript
// Order creation from invoice charge
const { data: order } = await supabase
  .from("orders")
  .insert({
    org_id: orgId,  // Inherited from invoice context
    user_id: invoice.user_id,
    service_id: item.service_id,
    // ... other fields
  });

// Subscription creation from recurring invoice
await supabase.from("subscriptions").insert({
  org_id: orgId,  // Inherited from invoice context
  user_id: invoice.user_id,
  invoice_id: invoice.id,
  // ... other fields
});
```

---

## Orders API

### Files Updated

| File | Changes |
|------|---------|
| `app/api/orders/route.ts` | Added authentication |
| `app/api/orders/[id]/route.ts` | Added authentication |
| `app/api/orders/list-orders.ts` | Added `orgId` parameter, filters count and data queries |
| `app/api/orders/create-order.ts` | Added `orgId` parameter, sets `org_id` on insert |
| `app/api/orders/retrieve-order.ts` | Added `orgId` parameter, filters by `org_id` |
| `app/api/orders/update-order.ts` | Added `orgId` parameter, filters by `org_id` |
| `app/api/orders/delete-order.ts` | Added `orgId` parameter, filters by `org_id` |

### Query Pattern for List with Pagination

```typescript
// Count query with org_id
let countQuery = supabase
  .from("orders")
  .select("*", { count: "exact", head: true })
  .eq("org_id", orgId)
  .is("deleted_at", null);

// Data query with org_id
let query = supabase
  .from("orders")
  .select("*")
  .eq("org_id", orgId)
  .is("deleted_at", null);
```

---

## Order Messages API

### Files Updated

| File | Changes |
|------|---------|
| `app/api/orders/[id]/messages/route.ts` | Added authentication |
| `app/api/orders/[id]/messages/list-order-messages.ts` | Added `orgId` parameter, validates order ownership |
| `app/api/orders/[id]/messages/create-order-message.ts` | Added `orgId` parameter, validates order ownership, sets `org_id` on insert |

### Implementation Details

Messages validate that the parent order belongs to the authenticated organization:

```typescript
// Verify order belongs to organization before listing/creating messages
const { data: order, error: orderError } = await supabase
  .from("orders")
  .select("id")
  .eq("id", order_id)
  .eq("org_id", orgId)  // Critical: ensures order belongs to tenant
  .is("deleted_at", null)
  .single();

if (orderError || !order) {
  return { error: "Not Found", status: 404 };
}

// Message created with org_id
const messageData = {
  org_id: orgId,
  order_id,
  user_id: finalUserId,
  message: input.message.trim(),
  // ... other fields
};
```

---

## Order Tasks API

### Files Updated

| File | Changes |
|------|---------|
| `app/api/orders/[id]/tasks/route.ts` | Added authentication |
| `app/api/orders/[id]/tasks/list-order-tasks.ts` | Added `orgId` parameter, validates order ownership |
| `app/api/orders/[id]/tasks/create-order-task.ts` | Added `orgId` parameter, validates order ownership, sets `org_id` on insert |

### Implementation Details

Tasks follow the same pattern as messages - validating parent order ownership:

```typescript
// Verify order belongs to organization
const { data: order, error: orderError } = await supabase
  .from("orders")
  .select("id")
  .eq("id", order_id)
  .eq("org_id", orgId)
  .is("deleted_at", null)
  .single();

// Task created with org_id
const taskData = {
  org_id: orgId,
  order_id,
  name: input.name.trim(),
  // ... other fields
};
```

---

## Session/Login Updates

### File: `app/login/actions.ts`

Updated to pass `org_id` when creating sessions:

```typescript
await createSession(user.id, user.org_id);
```

### File: `app/join/actions.ts`

Completely rewritten to:
1. Create organization first (if new)
2. Create user with `org_id` reference

```typescript
// Create organization
const { data: org } = await supabase
  .from("organizations")
  .insert({ name: orgName, slug: orgSlug })
  .select()
  .single();

// Create user with org_id
const { data: user } = await supabase
  .from("users")
  .insert({
    org_id: org.id,
    email: email,
    // ... other fields
  });
```

---

## Security Considerations

### Data Isolation

Every query that returns data now includes `.eq("org_id", orgId)` to ensure complete tenant isolation. This applies to:
- SELECT queries (list and retrieve operations)
- UPDATE queries (only update records belonging to the tenant)
- DELETE queries (soft delete only applies to tenant's records)

### Token Validation

API tokens are now scoped to organizations. When a token is validated:
1. The token hash is looked up in `api_tokens`
2. The associated `org_id` is retrieved
3. All subsequent operations are scoped to that organization

### Cross-Tenant Protection

Attempting to access resources from another organization returns `404 Not Found`, not `403 Forbidden`. This prevents information leakage about resource existence across tenants.

---

## Testing Multi-Tenancy

### Verify Isolation

To test that multi-tenancy is working correctly:

1. Create API tokens for different organizations
2. Create resources with Organization A's token
3. Attempt to retrieve/list those resources with Organization B's token
4. Verify Organization B receives empty results or 404 errors

### Example Test

```bash
# Create a client with Org A's token
curl -X POST https://api.example.com/api/clients \
  -H "Authorization: Bearer ORG_A_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "name_f": "Test"}'

# Try to retrieve with Org B's token (should return 404)
curl https://api.example.com/api/clients/CLIENT_ID \
  -H "Authorization: Bearer ORG_B_TOKEN"
# Expected: {"error": "Not Found"}
```

---

## Summary of Changes

| Category | Files Modified | Key Changes |
|----------|----------------|-------------|
| Database | 1 migration file | Created `organizations` table, added `org_id` to 13 tables |
| Authentication | `lib/auth.ts` | Returns `orgId` from token validation |
| Clients API | 7 files | Full multi-tenant support |
| Services API | 7 files | Full multi-tenant support (was previously unauthenticated) |
| Invoices API | 11 files | Full multi-tenant support including charge/mark_paid side effects |
| Orders API | 5 files | Full multi-tenant support |
| Order Messages | 3 files | Full multi-tenant support |
| Order Tasks | 3 files | Full multi-tenant support |
| Login/Join | 2 files | Updated session creation with org_id |

**Total: 40+ files modified** to implement comprehensive multi-tenant isolation across the entire API.
