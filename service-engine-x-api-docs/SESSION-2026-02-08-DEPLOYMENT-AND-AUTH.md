# Session: Deployment & Customer Auth

**Date:** 2026-02-08
**Scope:** Railway deployment, bug fixes, JWT auth system

---

## 1. Railway Deployment

Created a new Railway project (`service-engine-x-api-prod`) and deployed the FastAPI backend.

- **Project:** `service-engine-x-api-prod` ([Railway Dashboard](https://railway.com/project/cff73013-5938-4b79-94c0-1ca9351f7751))
- **Domain:** `api.serviceengine.xyz` (DNS confirmed pointing to Railway)
- **Railway URL:** `service-engine-x-api-prod-production.up.railway.app`

### Environment Variables Set

| Variable | Value |
|----------|-------|
| `SERVICE_ENGINE_X_SUPABASE_URL` | `https://htgfjmjuzcqffdzuiphg.supabase.co` |
| `SERVICE_ENGINE_X_SUPABASE_SERVICE_ROLE_KEY` | (set) |
| `API_BASE_URL` | `https://api.serviceengine.xyz` |
| `JWT_SECRET_KEY` | (set) |

### Deployment Issues Fixed

**Issue 1: Healthcheck failure.** Railway was checking `/api/health` but the app was listening on port `8000` while Railway assigns a dynamic `$PORT`. Fixed the Dockerfile to use shell form for variable expansion.

**Issue 2: `${PORT:-8000}` not expanding.** Railway runs start commands without a shell, so the bash default syntax was passed as a literal string. Fixed by wrapping in `sh -c`.

**Issue 3: Stale root `railway.json`.** The monorepo root had a `railway.json` from a previous setup with `cd service-engine-x-api` in the start command. Deleted it — the only Railway config is now `service-engine-x-api/railway.toml`.

---

## 2. Bug Fixes

### Currency Formatting (Pydantic ValidationError)

**Problem:** `/api/clients` returned 500 — `balance` field expected `str` but the DB returned `float` (`0.0`).

**Root Cause:** Supabase returns numeric columns as Python floats. The serialization layer used raw `str()` casts or `.get("field", "0.00")` passthrough, which doesn't handle the type mismatch.

**Fix:** Created `app/utils/formatting.py` with two shared utilities:

- `format_currency(value)` — always returns `"0.00"` format, handles float/int/str/None
- `format_currency_optional(value)` — same, but returns `None` when input is `None`

Applied across all 5 routers at every DB-to-API boundary:

| Router | Fields Fixed |
|--------|-------------|
| `clients.py` | `balance` |
| `invoices.py` | `amount`, `discount`, `discount2`, `total`, `subtotal`, `tax`, `credit`, `tax_percent`, `balance` |
| `tickets.py` | `balance`, `price` |
| `proposals.py` | `total`, `price` (serializers + public endpoint) |
| `services.py` | `format_pretty_price` refactored to use shared utility |

---

## 3. Customer Auth (JWT)

Implemented Option B — roll-your-own JWT auth using the existing `users` table. No Supabase Auth dependency.

### New Files

| File | Purpose |
|------|---------|
| `app/auth/jwt.py` | JWT creation and validation (HS256, 72h expiry) |
| `app/routers/auth.py` | `POST /api/auth/login` and `GET /api/auth/me` |
| `app/utils/formatting.py` | Shared currency formatting utilities |

### Modified Files

| File | Change |
|------|--------|
| `app/auth/dependencies.py` | Added `get_current_user` (JWT-only), `get_current_auth` (dual: JWT + API token) |
| `app/auth/__init__.py` | Exported new dependencies |
| `app/routers/__init__.py` | Registered `auth_router` |
| `app/main.py` | Added auth router, updated CORS origins |
| `app/config.py` | Added `jwt_secret_key`, `jwt_algorithm`, `jwt_expiration_hours` |
| `requirements.txt` | Added `PyJWT>=2.8.0` |
| `app/routers/engagements.py` | Switched to `get_current_auth` |
| `app/routers/projects.py` | Switched to `get_current_auth` |
| `app/routers/conversations.py` | Switched to `get_current_auth` |

### Auth Architecture

Three auth dependencies coexist:

| Dependency | Accepts | Used By |
|------------|---------|---------|
| `get_current_org` | API tokens only | Clients, services, orders, invoices, tickets, proposals (admin/machine endpoints) |
| `get_current_user` | JWTs only | `GET /api/auth/me` |
| `get_current_auth` | JWT first, API token fallback | Engagements, projects, conversations (portal + machine) |

### Endpoints

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| `POST` | `/api/auth/login` | None | Email + password → JWT |
| `GET` | `/api/auth/me` | JWT | Current user profile |

### Frontend Contract

```
1. POST /api/auth/login  { email, password }  →  { token, token_type, expires_in_hours, user }
2. Store token (localStorage, cookie, etc.)
3. All requests: Authorization: Bearer <jwt>
4. GET /api/auth/me to hydrate user state on app load
```

### CORS Origins Added

- `https://client.revenueactivation.com`
- `https://client.outboundsolutions.com`
- `https://outboundsolutions.com`

### Test Credentials

| Email | Password | Org | Role |
|-------|----------|-----|------|
| `testclient@example.com` | `clientpass123` | Revenue Activation | Client |

---

## 4. Cleanup

- Deleted stale `railway.json` from monorepo root
- Confirmed `api.serviceengine.xyz` DNS resolves to Railway (not Vercel)
- Identified `orgs` and `org_members` tables as dead weight (only `organizations` is used by the API)

---

## Verification

All tested against production (`api.serviceengine.xyz`):

| Test | Result |
|------|--------|
| `GET /api/health` | 200 — healthy |
| `POST /api/auth/login` (valid creds) | 200 — returns JWT + user |
| `POST /api/auth/login` (bad password) | 401 |
| `GET /api/auth/me` (JWT) | 200 — returns profile |
| `GET /api/engagements` (JWT) | 200 |
| `GET /api/projects` (JWT) | 200 |
| `GET /api/projects/{id}/conversations` (JWT) | 200 |
| `GET /api/engagements` (API token) | 200 |
| `GET /api/engagements` (no auth) | 401 |
| `GET /api/clients` (JWT) | 401 (correct — admin-only) |
| `GET /api/clients` (API token) | 200 |
