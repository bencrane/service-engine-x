# Service-Engine-X Infrastructure & Technology Stack

**Last Updated:** 2026-04-07

---

## Overview

Service-Engine-X uses a multi-service architecture with two separate API deployments, a PostgreSQL database, and various third-party integrations.

---

## Architecture Diagram

```
                                    ┌─────────────────────────────────────┐
                                    │           PRODUCTION                │
                                    └─────────────────────────────────────┘

    ┌─────────────────┐                                        ┌─────────────────┐
    │   Frontend      │                                        │   External      │
    │   (Client Apps) │                                        │   Services      │
    └────────┬────────┘                                        └────────┬────────┘
             │                                                          │
             ▼                                                          │
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │                              api.serviceengine.xyz                          │
    │                                                                             │
    │  ┌─────────────────────────────┐    ┌─────────────────────────────┐        │
    │  │      Next.js API Routes     │    │      FastAPI Backend        │        │
    │  │         (Vercel)            │    │        (Railway)            │        │
    │  │                             │    │                             │        │
    │  │  • /api/clients/*           │    │  • /api/proposals/*         │        │
    │  │  • /api/services/*          │    │  • /api/invoices/*          │        │
    │  │  • /api/orders/*            │    │  • /api/engagements/*       │        │
    │  │  • /api/tickets/*           │    │  • /api/public/*            │        │
    │  │  • Dashboard UI             │    │  • /api/webhooks/*          │        │
    │  │                             │    │  • /internal/*              │        │
    │  └──────────────┬──────────────┘    └──────────────┬──────────────┘        │
    │                 │                                   │                       │
    └─────────────────┼───────────────────────────────────┼───────────────────────┘
                      │                                   │
                      └───────────────┬───────────────────┘
                                      ▼
                      ┌───────────────────────────────────┐
                      │           Supabase                │
                      │      (PostgreSQL Database)        │
                      │                                   │
                      │  • Multi-tenant (org_id)          │
                      │  • Row-level isolation            │
                      │  • Real-time subscriptions        │
                      └───────────────────────────────────┘
```

---

## Technology Stack

### Backend Services

| Service | Technology | Hosting | Purpose |
|---------|------------|---------|---------|
| Primary API | Next.js 16+ API Routes | Vercel | Original API endpoints, dashboard UI |
| FastAPI Backend | FastAPI + Uvicorn | Railway | New endpoints, internal APIs, webhooks |
| Database | PostgreSQL 15 | Supabase | Primary data store |

### FastAPI Stack (this repository)

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | >=0.109.0 | Web framework |
| `uvicorn[standard]` | >=0.27.0 | ASGI server |
| `pydantic` | >=2.6.0 | Data validation |
| `pydantic-settings` | >=2.1.0 | Environment configuration |
| `supabase` | >=2.3.0 | Database client |
| `PyJWT` | >=2.8.0 | JWT token handling |
| `passlib[bcrypt]` | >=1.7.4 | Password hashing |
| `stripe` | >=7.0.0 | Payment processing |
| `resend` | >=0.7.0 | Transactional email |
| `docraptor` | >=2.0.0 | PDF generation |

### Next.js Stack (parent directory)

| Package | Version | Purpose |
|---------|---------|---------|
| `next` | 16.1.3+ | React framework |
| `react` | 19.2.3+ | UI library |
| `typescript` | 5.9.3+ | Type safety |
| `@supabase/supabase-js` | 2.90.1+ | Database client |
| `bcryptjs` | - | Password hashing |
| `tailwindcss` | - | Styling |

---

## Deployment Architecture

### Railway (FastAPI)

**Configuration:** `railway.toml`

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "sh -c 'uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}'"
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
```

**Key Points:**
- Uses Nixpacks for automatic dependency detection
- Uvicorn serves the FastAPI application
- Port is dynamically assigned by Railway via `$PORT`
- Auto-deploys on git push to main branch
- Currently **unexposed** (no public URL) - see [Known Issues](#known-issues)

**Dockerfile (alternative):**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

### Vercel (Next.js)

**Domain:** `api.serviceengine.xyz`

- Automatic deployments on git push
- Serverless functions for API routes
- Edge network for static assets
- Environment variables managed via Vercel dashboard

---

## Database (Supabase)

### Connection

**Environment Variables:**
```env
SUPABASE_URL=https://htgfjmjuzcqffdzuiphg.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service_role_jwt>
```

**FastAPI Client:** `app/database.py`
```python
from supabase import create_client, Client

def get_supabase() -> Client:
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    )
```

### Multi-Tenant Architecture

All tables use `org_id` for tenant isolation:

```sql
-- Every tenant-scoped table includes:
org_id UUID NOT NULL REFERENCES organizations(id)

-- Every query must filter by org_id:
SELECT * FROM accounts WHERE org_id = $1 AND id = $2;
```

See [MULTI-TENANT-ARCHITECTURE.md](./MULTI-TENANT-ARCHITECTURE.md) for complete patterns.

---

## Third-Party Integrations

| Service | Purpose | Configuration |
|---------|---------|---------------|
| **Stripe** | Payment processing (Checkout + Elements) | Per-org keys in `organizations` table |
| **Resend** | Transactional email | `RESEND_API_KEY` |
| **DocRaptor** | HTML to PDF conversion (signed PDFs) | `DOCRAPTOR_API_KEY` |
| **Cal.com** | Scheduling/booking | Webhook integration |

> **Note:** Documenso (e-signatures) code exists in the codebase but is dead — the only code path that calls it is unreachable. Stripe keys are stored **per-org** in the `organizations` table, not as app-level env vars.

---

## Environment Variables

### FastAPI (Railway)

```env
# Database
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# API Configuration
SERX_API_BASE_URL=https://api.serviceengine.xyz
DEBUG=false

# Third-Party Services
RESEND_API_KEY=re_...
DOCRAPTOR_API_KEY=...
# Note: Stripe keys are per-org, stored in organizations table (not env vars)
# Note: Documenso env vars exist in code but integration is dead/unused

# Internal Authentication
INTERNAL_API_KEY=...
```

### Next.js (Vercel)

```env
SERVICE_ENGINE_X_SUPABASE_URL=https://xxx.supabase.co
SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY=eyJ...
SERVICE_ENGINE_X_SUPABASE_ANON_KEY=eyJ...
```

---

## API Endpoint Distribution

### Next.js (Vercel) - `api.serviceengine.xyz`

| Resource | Endpoints | Status |
|----------|-----------|--------|
| Clients | 5 | Active |
| Services | 5 | Active |
| Orders | 5 | Active |
| Order Tasks | 4 | Active |
| Order Messages | 1 | Active |
| Tickets | 5 | Active |
| Dashboard UI | - | Active |

### FastAPI (Railway)

| Resource | Endpoints | Status |
|----------|-----------|--------|
| Proposals | 6 | Active |
| Invoices | 7 | Active |
| Engagements | CRUD | Active |
| Accounts | CRUD | Active |
| Contacts | CRUD | Active |
| Public APIs | 4 | Active (GET, sign, checkout, payment-intent) |
| Webhooks | 1 | Active (Stripe: checkout.session.completed + payment_intent.succeeded) |
| Internal Admin | 2 | Active |

---

## Local Development

### FastAPI

```bash
cd service-engine-x-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with real values

# Run development server
uvicorn app.main:app --reload --port 8000
```

### Next.js

```bash
cd service-engine-x

# Install dependencies
npm install

# Run development server
npm run dev
```

---

## Known Issues

### Dual API Architecture

**Problem:** The project has two separate API backends:
1. Next.js API routes on Vercel (public at `api.serviceengine.xyz`)
2. FastAPI on Railway (currently unexposed)

**Impact:** New FastAPI endpoints are not accessible at the production URL.

**Solutions:**

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A | Expose FastAPI on Railway | Quick, no code changes | Two different API URLs |
| B | Add routes to Next.js | Single API URL | Code duplication |
| C | Migrate everything to FastAPI | Single source of truth | Large migration effort |
| D | Proxy from Next.js to FastAPI | Gradual migration | Added latency |

See [DEPLOYMENT-ARCHITECTURE-ISSUE.md](../../service-engine-x-api-docs/DEPLOYMENT-ARCHITECTURE-ISSUE.md) for full details.

---

## What This Project Does NOT Use

- **Modal** - Not used in this project (no serverless GPU/CPU functions)
- **AWS Lambda** - Using Railway/Vercel instead
- **Docker Compose** - Railway uses Nixpacks; docker-compose.yml exists for local development only
- **Redis** - No caching layer currently
- **Kubernetes** - Using PaaS (Railway/Vercel) instead

---

## Project Structure

```
/service-engine-x/                    # Root monorepo
├── app/                              # Next.js App Router (Vercel)
│   └── api/                          # Next.js API routes
├── service-engine-x-api/             # FastAPI backend (Railway) ← YOU ARE HERE
│   ├── app/
│   │   ├── main.py                   # FastAPI application
│   │   ├── config.py                 # Pydantic settings
│   │   ├── database.py               # Supabase client
│   │   ├── auth/                     # Authentication
│   │   ├── models/                   # Pydantic schemas
│   │   ├── routers/                  # API endpoints
│   │   ├── services/                 # External service integrations
│   │   └── utils/                    # Helpers
│   ├── docs/                         # Documentation
│   ├── tests/                        # Pytest tests
│   ├── requirements.txt              # Python dependencies
│   ├── railway.toml                  # Railway configuration
│   └── Dockerfile                    # Container definition
├── service-engine-x-api-docs/        # API documentation
└── migrations/                       # SQL migrations
```

---

## References

- [Railway Documentation](https://docs.railway.app/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vercel Documentation](https://vercel.com/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Multi-Tenant Architecture Guide](./MULTI-TENANT-ARCHITECTURE.md)
- [Authentication Guide](./AUTHENTICATION.md)
