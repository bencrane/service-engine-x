# Service-Engine-X: Complete Project Guide

**Version:** 1.0.0
**Last Updated:** 2026-02-07
**Purpose:** Comprehensive reference for understanding and extending this API project

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure](#3-project-structure)
4. [Authentication System](#4-authentication-system)
5. [Database Architecture](#5-database-architecture)
6. [API Design Patterns](#6-api-design-patterns)
7. [OpenAPI Specification System](#7-openapi-specification-system)
8. [Implementing New Endpoints](#8-implementing-new-endpoints)
9. [Response Formats](#9-response-formats)
10. [Error Handling](#10-error-handling)
11. [Implementation Status](#11-implementation-status)
12. [File Reference](#12-file-reference)

---

## 1. Project Overview

### What Is This?

Service-Engine-X is a **REST API platform** for managing a business service engine system. It provides:

- **Client Management** - Customer records with addresses, billing, and custom fields
- **Service Catalog** - Purchasable products with pricing configurations
- **Order Management** - Core transaction entity linking clients to services
- **Invoice System** - Billing with charge and payment tracking
- **Ticket System** - Customer support workflows
- **Task Management** - Work items attached to orders

### Core Principles

1. **API-First Design** - Complete OpenAPI 3.1 specification for all endpoints
2. **Bearer Token Authentication** - SHA-256 hashed tokens with expiration
3. **Consistent Response Shapes** - All list endpoints return `{ data, links, meta }`
4. **Soft Deletes** - Entities use `deleted_at` rather than hard deletion
5. **UUID Primary Keys** - All entities use UUIDs, never sequential integers

### Production URL

```
https://api.serviceengine.xyz
```

---

## 2. Technology Stack

### Core Framework

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 16.1.3+ | React framework with App Router |
| React | 19.2.3+ | UI library |
| TypeScript | 5.9.3+ | Type safety |
| Supabase | 2.90.1+ | PostgreSQL database + auth |

### Supporting Libraries

| Library | Purpose |
|---------|---------|
| `bcryptjs` | Password hashing (10 rounds) |
| `tailwindcss` | Styling (admin dashboard) |
| `lucide-react` | Icons |
| `class-variance-authority` | Component variants |

### Development

```bash
npm run dev    # Start development server (Turbopack enabled)
npm run build  # Production build
npm run start  # Start production server
npm run lint   # ESLint
```

---

## 3. Project Structure

```
/service-engine-x/
│
├── app/                              # Next.js App Router
│   ├── api/                          # REST API endpoints
│   │   ├── route.ts                  # GET /api - Index/health check
│   │   ├── clients/                  # Client CRUD
│   │   │   ├── route.ts              # GET/POST /api/clients
│   │   │   ├── [id]/route.ts         # GET/PATCH/DELETE /api/clients/{id}
│   │   │   ├── list-clients.ts       # Implementation
│   │   │   ├── create-client.ts
│   │   │   ├── retrieve-client.ts
│   │   │   ├── update-client.ts
│   │   │   └── delete-client.ts
│   │   ├── services/                 # Service CRUD (same pattern)
│   │   ├── orders/                   # Order CRUD + nested resources
│   │   │   ├── [id]/
│   │   │   │   ├── messages/         # Order messages
│   │   │   │   └── tasks/            # Order tasks
│   │   ├── order-messages/           # Standalone message operations
│   │   ├── order-tasks/              # Standalone task operations
│   │   ├── invoices/                 # Invoice CRUD + actions
│   │   │   ├── [id]/
│   │   │   │   ├── charge/           # POST /api/invoices/{id}/charge
│   │   │   │   └── mark_paid/        # POST /api/invoices/{id}/mark_paid
│   │   └── tickets/                  # Ticket CRUD
│   │
│   ├── dashboard/                    # Admin UI (22 pages)
│   ├── login/                        # Auth pages
│   ├── join/                         # Registration
│   ├── actions/                      # Server actions
│   └── layout.tsx                    # Root layout
│
├── lib/                              # Shared utilities
│   ├── auth.ts                       # Authentication functions
│   ├── supabase.ts                   # Database client
│   └── utils.ts                      # Helper functions
│
├── openapi/                          # OpenAPI 3.1 specification
│   ├── index.ts                      # Core registry + types
│   ├── register.ts                   # Route registration
│   ├── schemas/                      # Shared schemas
│   └── routes/                       # Per-endpoint metadata
│       ├── clients/
│       ├── services/
│       ├── orders/
│       └── health/
│
├── service-engine-x-api-docs/        # API documentation (Markdown)
│   ├── clients/                      # 5 endpoint docs
│   ├── services/                     # 5 endpoint docs
│   ├── orders/                       # 5 endpoint docs
│   ├── invoices/                     # 7 endpoint docs
│   ├── order-tasks/                  # 6 endpoint docs
│   ├── order-messages/               # 3 endpoint docs
│   ├── tickets/                      # 5 endpoint docs
│   ├── IMPLEMENTATION-STATUS.md      # Progress tracker
│   └── PROJECT-GUIDE.md              # This file
│
├── reference-docs/                   # Development guides
│   └── mcp-tools-guide.md
│
├── schema-and-build-plan.md          # Architecture overview
├── phase-1-schema-plan.md            # Foundation tables
├── phase-2-schema-plan.md            # Clients
├── phase-3-schema-plan.md            # Services
├── phase-4-schema-plan.md            # Orders
├── phase-5-schema-plan.md            # Order dependents
├── phase-6-schema-plan.md            # Financial
├── phase-7-schema-plan.md            # Support
│
├── package.json
├── tsconfig.json
├── next.config.ts                    # Turbopack enabled
└── .env.local                        # Environment variables
```

---

## 4. Authentication System

### Overview

The API uses **Bearer token authentication**. Tokens are stored hashed (SHA-256) in the `api_tokens` table.

### Token Flow

```
1. Client sends: Authorization: Bearer {plaintext_token}
2. Server extracts token from header
3. Server hashes token with SHA-256
4. Server queries api_tokens table for matching hash
5. Server validates expiration (expires_at)
6. Server updates last_used_at timestamp
7. Server returns user_id for authorization
```

### Implementation Files

**Primary:** `/lib/auth.ts`

```typescript
// Token extraction
export function extractBearerToken(authHeader: string | null): string | null {
  if (!authHeader?.startsWith("Bearer ")) {
    return null;
  }
  return authHeader.slice(7);
}

// Token validation
export async function validateApiToken(token: string): Promise<ApiAuthResult> {
  // 1. Hash the token
  const encoder = new TextEncoder();
  const data = encoder.encode(token);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const tokenHash = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");

  // 2. Query database
  const { data: tokenRecord, error } = await supabase
    .from("api_tokens")
    .select("id, user_id, expires_at")
    .eq("token_hash", tokenHash)
    .single();

  // 3. Validate expiration
  if (tokenRecord.expires_at && new Date(tokenRecord.expires_at) < new Date()) {
    return { valid: false, userId: null, error: "Token expired" };
  }

  // 4. Update last_used_at
  await supabase
    .from("api_tokens")
    .update({ last_used_at: new Date().toISOString() })
    .eq("id", tokenRecord.id);

  return { valid: true, userId: tokenRecord.user_id };
}
```

### ApiAuthResult Interface

```typescript
interface ApiAuthResult {
  valid: boolean;
  userId: string | null;
  error?: string;
}
```

### Session Authentication (Dashboard)

For the admin dashboard, session-based auth is used:

```typescript
// Create session (login)
export async function createSession(userId: string): Promise<string> {
  const token = randomBytes(32).toString("hex");
  const expiresAt = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000); // 30 days

  await supabase.from("sessions").insert({
    user_id: userId,
    token,
    expires_at: expiresAt.toISOString(),
  });

  // Set HTTP-only cookie
  cookieStore.set("session", token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    expires: expiresAt,
    path: "/",
  });

  return token;
}

// Get session
export async function getSession() {
  const token = cookieStore.get("session")?.value;
  if (!token) return null;

  const { data: session } = await supabase
    .from("sessions")
    .select("*, users(*)")
    .eq("token", token)
    .gt("expires_at", new Date().toISOString())
    .single();

  return session;
}

// Destroy session (logout)
export async function destroySession() {
  const token = cookieStore.get("session")?.value;
  if (token) {
    await supabase.from("sessions").delete().eq("token", token);
    cookieStore.delete("session");
  }
}
```

### Password Hashing

```typescript
export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 10);
}

export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash);
}
```

---

## 5. Database Architecture

### Design Principles

1. **UUID Primary Keys** - All tables use `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`
2. **Soft Deletes** - Use `deleted_at` timestamp instead of hard deletion
3. **Unified Users Table** - Team and clients share `users` table, differentiated by `role_id`
4. **Junction Tables** - Many-to-many relationships use explicit junction tables
5. **JSONB Storage** - Metadata, custom_fields, and form_data stored as JSON

### Database Connection

**File:** `/lib/supabase.ts`

```typescript
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.SERVICE_ENGINE_X_SUPABASE_URL!;
const supabaseServiceKey = process.env.SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY!;

export const supabase = createClient(supabaseUrl, supabaseServiceKey);
```

### Environment Variables

```env
SERVICE_ENGINE_X_SUPABASE_URL=https://htgfjmjuzcqffdzuiphg.supabase.co
SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY=<service_role_jwt>
SERVICE_ENGINE_X_SUPABASE_ANON_KEY=<anon_jwt>
```

### Schema Phases

The database was built in phases to ensure upstream dependencies exist before downstream entities:

| Phase | Tables | Purpose |
|-------|--------|---------|
| 1 | `roles`, `users`, `tags` | Foundation - referenced by everything |
| 2 | `addresses` | Client infrastructure |
| 3 | `services` | Product catalog |
| 4 | `orders`, `order_items`, `order_employees`, `order_tags` | Economic core |
| 5 | `order_tasks`, `order_messages` | Order dependents |
| 6 | `invoices`, `invoice_items`, `subscriptions` | Financial layer |
| 7 | `tickets`, `ticket_messages` | Support system |
| 8 | `forms`, `filled_forms`, `client_activities`, `logs`, `sessions`, `api_tokens` | Auxiliary |

### Key Tables

#### users

Unified table for both team members and clients.

```sql
id UUID PRIMARY KEY
email VARCHAR UNIQUE NOT NULL
password_hash VARCHAR
name_f VARCHAR NOT NULL
name_l VARCHAR NOT NULL
company VARCHAR
phone VARCHAR
role_id UUID REFERENCES roles(id)
status INTEGER DEFAULT 1
balance DECIMAL(10,2) DEFAULT 0
spent DECIMAL(10,2)
stripe_id VARCHAR
custom_fields JSONB DEFAULT '{}'
address_id UUID REFERENCES addresses(id)
created_at TIMESTAMP DEFAULT NOW()
updated_at TIMESTAMP DEFAULT NOW()
deleted_at TIMESTAMP
```

**Team vs Client Differentiation:**
- Team members have `role.dashboard_access > 0`
- Clients have `role.dashboard_access = 0`

#### roles

Permission sets with 16 boolean settings and 10 level-based permissions (0-3).

```sql
id UUID PRIMARY KEY
name VARCHAR NOT NULL
dashboard_access INTEGER DEFAULT 0  -- 0=client, 1+=team
order_access INTEGER DEFAULT 0
order_management INTEGER DEFAULT 0
ticket_access INTEGER DEFAULT 0
ticket_management INTEGER DEFAULT 0
invoice_access INTEGER DEFAULT 0
invoice_management INTEGER DEFAULT 0
clients INTEGER DEFAULT 0
services INTEGER DEFAULT 0
coupons INTEGER DEFAULT 0
forms INTEGER DEFAULT 0
messaging INTEGER DEFAULT 0
affiliates INTEGER DEFAULT 0
settings_company BOOLEAN DEFAULT FALSE
settings_payments BOOLEAN DEFAULT FALSE
settings_team BOOLEAN DEFAULT FALSE
-- ... (16 boolean settings total)
created_at TIMESTAMP DEFAULT NOW()
updated_at TIMESTAMP DEFAULT NOW()
```

#### orders

Central transaction entity.

```sql
id UUID PRIMARY KEY
user_id UUID NOT NULL REFERENCES users(id)  -- The client
service_id UUID REFERENCES services(id)
service VARCHAR  -- Fallback name if service_id null
status INTEGER DEFAULT 0
total DECIMAL(10,2)
currency VARCHAR(3) DEFAULT 'USD'
form_data JSONB
metadata JSONB
notes TEXT
created_at TIMESTAMP DEFAULT NOW()
updated_at TIMESTAMP DEFAULT NOW()
deleted_at TIMESTAMP
```

#### api_tokens

Bearer token storage.

```sql
id UUID PRIMARY KEY
user_id UUID NOT NULL REFERENCES users(id)
token_hash VARCHAR NOT NULL  -- SHA-256 hash
name VARCHAR  -- User-friendly label
expires_at TIMESTAMP
last_used_at TIMESTAMP
created_at TIMESTAMP DEFAULT NOW()
```

---

## 6. API Design Patterns

### Route File Organization

Each endpoint domain follows this pattern:

```
/app/api/{domain}/
├── route.ts              # Handles collection routes (GET list, POST create)
├── [id]/route.ts         # Handles item routes (GET retrieve, PATCH update, DELETE)
├── list-{domain}.ts      # List implementation
├── create-{domain}.ts    # Create implementation
├── retrieve-{domain}.ts  # Retrieve implementation
├── update-{domain}.ts    # Update implementation
└── delete-{domain}.ts    # Delete implementation
```

### Route Handler Pattern

**File:** `/app/api/clients/route.ts`

```typescript
import { NextRequest, NextResponse } from "next/server";
import { listClients } from "./list-clients";
import { createClient } from "./create-client";
import { validateApiToken, extractBearerToken } from "@/lib/auth";

export async function GET(request: NextRequest) {
  // 1. Extract token
  const token = extractBearerToken(request.headers.get("authorization"));
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  // 2. Validate token
  const auth = await validateApiToken(token);
  if (!auth.valid) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  // 3. Delegate to implementation
  return listClients(request, auth.userId);
}

export async function POST(request: NextRequest) {
  const token = extractBearerToken(request.headers.get("authorization"));
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const auth = await validateApiToken(token);
  if (!auth.valid) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  return createClient(request, auth.userId);
}
```

### Pagination Pattern

All list endpoints support consistent pagination:

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `limit` | integer | 20 | 100 | Items per page |
| `page` | integer | 1 | - | Page number (1-indexed) |
| `sort` | string | `created_at:desc` | - | Sort field and direction |

**Implementation:**

```typescript
const limit = Math.min(Math.max(parseInt(searchParams.get("limit") || "20", 10), 1), 100);
const page = Math.max(parseInt(searchParams.get("page") || "1", 10), 1);
const offset = (page - 1) * limit;

const sortParam = searchParams.get("sort") || "created_at:desc";
const [sortField, sortDirection] = sortParam.split(":");
const ascending = sortDirection === "asc";
```

### Filtering Pattern

Filters use a bracket-notation syntax:

```
filters[{field}][{operator}]=value
```

**Supported Operators:**

| Operator | Meaning | Example |
|----------|---------|---------|
| `$eq` | Equals | `filters[status][$eq]=1` |
| `$lt` | Less than | `filters[balance][$lt]=100` |
| `$gt` | Greater than | `filters[balance][$gt]=0` |
| `$in[]` | In array | `filters[id][$in][]=uuid1&filters[id][$in][]=uuid2` |

**Implementation:**

```typescript
for (const [key, value] of searchParams.entries()) {
  const filterMatch = key.match(/^filters\[(\w+)\]\[(\$\w+)\](\[\])?$/);
  if (filterMatch) {
    const [, field, operator] = filterMatch;
    const filterableFields = ["id", "email", "status", "balance", "created_at"];
    if (!filterableFields.includes(field)) continue;

    switch (operator) {
      case "$eq":
        query = query.eq(field, value);
        break;
      case "$lt":
        query = query.lt(field, value);
        break;
      case "$gt":
        query = query.gt(field, value);
        break;
      case "$in":
        const inValues = searchParams.getAll(`filters[${field}][$in][]`);
        if (inValues.length > 0) {
          query = query.in(field, inValues);
        }
        break;
    }
  }
}
```

### Sorting Pattern

Sort parameter format: `field:direction`

- `created_at:desc` (default)
- `name_f:asc`
- `status:desc`

Only stored database fields can be sorted (not computed fields like `name`).

---

## 7. OpenAPI Specification System

### Architecture

The OpenAPI spec is built at runtime through explicit registration, not filesystem scanning.

**Files:**
- `/openapi/index.ts` - Core registry, types, and helper functions
- `/openapi/register.ts` - Imports and registers all routes
- `/openapi/schemas/` - Shared schema definitions
- `/openapi/routes/{domain}/{endpoint}.ts` - Per-endpoint metadata

### Core Registry

**File:** `/openapi/index.ts`

```typescript
export interface OpenAPISpec {
  openapi: string;
  info: { title: string; version: string; description?: string };
  servers: Array<{ url: string; description?: string }>;
  security: Array<Record<string, string[]>>;
  components: {
    securitySchemes: Record<string, {...}>;
    schemas: Record<string, object>;
  };
  paths: Record<string, Record<string, object>>;
}

export const openapi: OpenAPISpec = {
  openapi: "3.1.0",
  info: {
    title: "ServiceEngineX API",
    version: "1.0.0",
    description: "API for ServiceEngineX platform",
  },
  servers: [{ url: "https://api.serviceengine.xyz", description: "Production API" }],
  security: [{ BearerAuth: [] }],
  components: {
    securitySchemes: {
      BearerAuth: {
        type: "http",
        scheme: "bearer",
        bearerFormat: "JWT",
        description: "Bearer token authentication",
      },
    },
    schemas: {},
  },
  paths: {},
};

export function registerRoute(metadata: RouteMetadata): void {
  const { method, path, ...operation } = metadata;
  const methodLower = method.toLowerCase();
  if (!openapi.paths[path]) openapi.paths[path] = {};
  openapi.paths[path][methodLower] = operation;
}

export function getEndpointList(): EndpointSummary[] {
  const endpoints: EndpointSummary[] = [];
  for (const [path, methods] of Object.entries(openapi.paths)) {
    for (const [method, operation] of Object.entries(methods)) {
      endpoints.push({
        method: method.toUpperCase(),
        path,
        description: operation.summary || operation.description || "",
      });
    }
  }
  return endpoints.sort((a, b) => a.path.localeCompare(b.path));
}
```

### Route Metadata Interface

```typescript
export interface RouteMetadata {
  method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  path: string;
  summary: string;
  description?: string;
  tags?: string[];
  operationId?: string;
  parameters?: Array<{
    name: string;
    in: "query" | "path" | "header";
    required?: boolean;
    description?: string;
    schema: object;
  }>;
  requestBody?: {
    required?: boolean;
    description?: string;
    content: { "application/json": { schema: object } };
  };
  responses: Record<string, {
    description: string;
    content?: { "application/json": { schema: object } };
  }>;
}
```

### Route Registration

**File:** `/openapi/register.ts`

```typescript
import { openapi, registerRoute } from "./index";
import { schemas } from "./schemas";

// Import all route metadata
import { openapi as listClients } from "./routes/clients/list-clients";
import { openapi as createClient } from "./routes/clients/create-client";
// ... all other routes

function registerSchemas(): void {
  Object.assign(openapi.components.schemas, schemas);
}

function registerAllRoutes(): void {
  registerRoute(listClients);
  registerRoute(createClient);
  // ... all other routes
}

export function initializeOpenAPI(): void {
  registerSchemas();
  registerAllRoutes();
}

// Auto-initialize on import
initializeOpenAPI();
```

### Example Route Metadata

**File:** `/openapi/routes/clients/list-clients.ts`

```typescript
import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "GET",
  path: "/api/clients",
  summary: "List all clients",
  description: "Returns a paginated list of all clients.",
  tags: ["Clients"],
  operationId: "listClients",
  parameters: [
    {
      name: "limit",
      in: "query",
      required: false,
      description: "Items per page",
      schema: { type: "integer", default: 10 },
    },
    {
      name: "page",
      in: "query",
      required: false,
      description: "Page number",
      schema: { type: "integer", default: 1 },
    },
    {
      name: "sort",
      in: "query",
      required: false,
      description: "Sort by fields (e.g., id:desc)",
      schema: { type: "string" },
    },
    {
      name: "filters[email][$eq]",
      in: "query",
      required: false,
      description: "Filter by email",
      schema: { type: "string" },
    },
  ],
  responses: {
    "200": {
      description: "Successful response",
      content: {
        "application/json": {
          schema: {
            type: "object",
            properties: {
              data: { type: "array", items: { $ref: "#/components/schemas/Client" } },
              links: { $ref: "#/components/schemas/PaginationLinks" },
              meta: { $ref: "#/components/schemas/PaginationMeta" },
            },
          },
        },
      },
    },
    "401": { description: "Unauthorized" },
  },
};
```

### API Index Endpoint

**File:** `/app/api/route.ts`

Returns HTML for browsers, JSON for API clients:

```typescript
import { getEndpointList } from "@/openapi";
import "@/openapi/register"; // Triggers registration

export async function GET(request: NextRequest) {
  const endpoints = getEndpointList();
  const accept = request.headers.get("accept") || "";

  if (accept.includes("application/json") && !accept.includes("text/html")) {
    return NextResponse.json({
      name: "ServiceEngine API",
      version: "1.0.0",
      status: "running",
      endpoints,
    });
  }

  // Return HTML table of all endpoints
  return new NextResponse(html, { headers: { "Content-Type": "text/html" } });
}
```

---

## 8. Implementing New Endpoints

### Step-by-Step Guide

#### 1. Create Documentation

Create a Markdown file in `/service-engine-x-api-docs/{domain}/{action}.md`:

```markdown
# Action Name

```
METHOD /api/path
```

## 1. Purpose
What this endpoint does.

## 2. Authorization
Requires Bearer token...

## 3. Request Parameters
Tables of query params, path params, body fields...

## 4. Side Effects
Database changes, notifications, etc.

## 5. Response Shape
JSON examples with field descriptions...

## 6. Field Semantics
Read-only vs read-write, computed fields...

## 7. Error Behavior
Error codes and response formats...

## 8. Notes / Edge Cases
Special handling, gotchas...
```

#### 2. Create OpenAPI Metadata

Create `/openapi/routes/{domain}/{action}.ts`:

```typescript
import { RouteMetadata } from "../../index";

export const openapi: RouteMetadata = {
  method: "POST",
  path: "/api/orders",
  summary: "Create order",
  description: "Creates a new order for a client.",
  tags: ["Orders"],
  operationId: "createOrder",
  requestBody: {
    required: true,
    content: {
      "application/json": {
        schema: {
          type: "object",
          required: ["user_id", "service_id"],
          properties: {
            user_id: { type: "string", format: "uuid" },
            service_id: { type: "string", format: "uuid" },
          },
        },
      },
    },
  },
  responses: {
    "201": {
      description: "Order created",
      content: {
        "application/json": {
          schema: { $ref: "#/components/schemas/Order" },
        },
      },
    },
    "401": { description: "Unauthorized" },
    "422": { description: "Validation error" },
  },
};
```

#### 3. Register the Route

Add import and registration to `/openapi/register.ts`:

```typescript
import { openapi as createOrder } from "./routes/orders/create-order";

function registerAllRoutes(): void {
  // ... existing routes
  registerRoute(createOrder);
}
```

#### 4. Create Implementation File

Create `/app/api/{domain}/{action}.ts`:

```typescript
import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

export async function createOrder(request: NextRequest, ownerId: string | null) {
  // 1. Parse request body
  const body = await request.json();

  // 2. Validate required fields
  if (!body.user_id || !body.service_id) {
    return NextResponse.json(
      { message: "Invalid request parameters.", errors: { user_id: ["Required"] } },
      { status: 422 }
    );
  }

  // 3. Insert into database
  const { data: order, error } = await supabase
    .from("orders")
    .insert({
      user_id: body.user_id,
      service_id: body.service_id,
      status: 0,
    })
    .select()
    .single();

  if (error) {
    return NextResponse.json({ error: "Database error" }, { status: 500 });
  }

  // 4. Return response
  return NextResponse.json({ data: serializeOrder(order) }, { status: 201 });
}

function serializeOrder(order: OrderRow) {
  return {
    id: order.id,
    user_id: order.user_id,
    service_id: order.service_id,
    status: order.status,
    created_at: order.created_at,
  };
}
```

#### 5. Create Route Handler

Create or update `/app/api/{domain}/route.ts`:

```typescript
import { NextRequest, NextResponse } from "next/server";
import { createOrder } from "./create-order";
import { listOrders } from "./list-orders";
import { validateApiToken, extractBearerToken } from "@/lib/auth";

export async function GET(request: NextRequest) {
  const token = extractBearerToken(request.headers.get("authorization"));
  if (!token) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const auth = await validateApiToken(token);
  if (!auth.valid) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  return listOrders(request, auth.userId);
}

export async function POST(request: NextRequest) {
  const token = extractBearerToken(request.headers.get("authorization"));
  if (!token) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const auth = await validateApiToken(token);
  if (!auth.valid) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  return createOrder(request, auth.userId);
}
```

#### 6. Update Implementation Status

Update `/service-engine-x-api-docs/IMPLEMENTATION-STATUS.md` to reflect the new endpoint.

---

## 9. Response Formats

### List Response (Paginated)

All list endpoints return this structure:

```json
{
  "data": [
    { /* entity object */ },
    { /* entity object */ }
  ],
  "links": {
    "first": "https://api.serviceengine.xyz/api/clients?page=1&limit=20",
    "last": "https://api.serviceengine.xyz/api/clients?page=5&limit=20",
    "prev": null,
    "next": "https://api.serviceengine.xyz/api/clients?page=2&limit=20"
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "to": 20,
    "last_page": 5,
    "per_page": 20,
    "total": 100,
    "path": "https://api.serviceengine.xyz/api/clients",
    "links": [
      { "url": null, "label": "Previous", "active": false },
      { "url": "...?page=1", "label": "1", "active": true },
      { "url": "...?page=2", "label": "2", "active": false },
      { "url": "...?page=2", "label": "Next", "active": false }
    ]
  }
}
```

### Single Entity Response

```json
{
  "data": { /* entity object */ }
}
```

### Create Response

```json
{
  "data": { /* created entity */ }
}
```

Status: `201 Created`

### Update Response

```json
{
  "data": { /* updated entity */ }
}
```

Status: `200 OK`

### Delete Response

```json
{
  "message": "Client deleted successfully"
}
```

Status: `200 OK`

### Empty List

```json
{
  "data": [],
  "links": { ... },
  "meta": { "total": 0, ... }
}
```

Never returns `null` for data - always an empty array.

---

## 10. Error Handling

### 401 Unauthorized

Missing or invalid Bearer token.

```json
{
  "error": "Unauthorized"
}
```

**Causes:**
- No `Authorization` header
- Token doesn't start with `Bearer `
- Token hash not found in database
- Token expired (`expires_at` in past)

### 404 Not Found

Resource doesn't exist.

```json
{
  "error": "Client not found"
}
```

### 422 Unprocessable Entity

Validation errors.

```json
{
  "message": "Invalid request parameters.",
  "errors": {
    "email": ["Email is required", "Invalid email format"],
    "name_f": ["First name is required"]
  }
}
```

### 500 Internal Server Error

Database or server errors.

```json
{
  "error": "Database error"
}
```

---

## 11. Implementation Status

### Summary (as of 2026-02-07)

| Category | Implemented | Not Implemented | Total |
|----------|-------------|-----------------|-------|
| Clients | 5 | 0 | 5 |
| Services | 5 | 0 | 5 |
| **Orders** | **0** | **5** | **5** |
| Order Messages | 3 | 0 | 3 |
| Order Tasks | 6 | 0 | 6 |
| Invoices | 7 | 0 | 7 |
| **Tickets** | **0** | **5** | **5** |
| **TOTAL** | **26** | **10** | **36** |

### Fully Implemented

- **Clients:** List, Create, Retrieve, Update, Delete
- **Services:** List, Create, Retrieve, Update, Delete
- **Order Messages:** List, Create, Delete
- **Order Tasks:** List, Create, Update, Delete, Mark Complete, Mark Incomplete
- **Invoices:** List, Create, Retrieve, Update, Delete, Charge, Mark Paid

### Not Implemented (High Priority)

**Orders (5 endpoints):**
- `GET /api/orders` - List orders
- `POST /api/orders` - Create order
- `GET /api/orders/{id}` - Retrieve order
- `PATCH /api/orders/{id}` - Update order
- `DELETE /api/orders/{id}` - Delete order

**Tickets (5 endpoints):**
- `GET /api/tickets` - List tickets
- `POST /api/tickets` - Create ticket
- `GET /api/tickets/{id}` - Retrieve ticket
- `PATCH /api/tickets/{id}` - Update ticket
- `DELETE /api/tickets/{id}` - Delete ticket

Documentation exists for all unimplemented endpoints in `/service-engine-x-api-docs/`.

---

## 12. File Reference

### Critical Files

| File | Purpose |
|------|---------|
| `/lib/auth.ts` | All authentication logic (tokens, sessions, passwords) |
| `/lib/supabase.ts` | Database client initialization |
| `/openapi/index.ts` | OpenAPI registry and types |
| `/openapi/register.ts` | Route registration |
| `/app/api/route.ts` | API index/health endpoint |

### Configuration Files

| File | Purpose |
|------|---------|
| `package.json` | Dependencies and scripts |
| `tsconfig.json` | TypeScript configuration |
| `next.config.ts` | Next.js configuration (Turbopack) |
| `.env.local` | Environment variables (Supabase keys) |

### Documentation Files

| File | Purpose |
|------|---------|
| `/service-engine-x-api-docs/IMPLEMENTATION-STATUS.md` | Progress tracker |
| `/service-engine-x-api-docs/PROJECT-GUIDE.md` | This file |
| `/schema-and-build-plan.md` | Database architecture overview |
| `/phase-{1-7}-schema-plan.md` | Per-phase schema details |

### Path Alias

TypeScript path alias configured in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

Usage: `import { supabase } from "@/lib/supabase"`

---

## Quick Reference Card

### Authentication

```bash
# Required header on all requests
Authorization: Bearer {your_api_token}
```

### Common Patterns

```bash
# List with pagination
GET /api/clients?page=1&limit=20&sort=created_at:desc

# Filter
GET /api/clients?filters[status][$eq]=1&filters[balance][$gt]=0

# Create
POST /api/clients
Content-Type: application/json
{ "email": "...", "name_f": "...", "name_l": "..." }

# Update
PATCH /api/clients/{id}
Content-Type: application/json
{ "name_f": "Updated" }

# Delete
DELETE /api/clients/{id}
```

### Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 401 | Unauthorized |
| 404 | Not found |
| 422 | Validation error |
| 500 | Server error |

---

*This guide is the authoritative reference for the Service-Engine-X API project. Keep it updated as the system evolves.*
