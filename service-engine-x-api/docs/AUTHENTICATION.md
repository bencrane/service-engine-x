Updated: Saturday, April 25, 2026 at 7:14 PM EDT

# Authentication Guide

This document describes the authentication system used by the Service Engine X (SERX) API as of Phase 2 of the auth remediation work.

For the full Phase 1+2 remediation history, scope, files changed, what is NOT yet done, and the operator readiness sequence into Phase 3, see [`SERX_AUTH_REMEDIATION_PHASE_1_2.md`](../../docs/SERX_AUTH_REMEDIATION_PHASE_1_2.md).

> **Status (post-Phase 2):** transitional. Routes accept either the legacy `SERX_AUTH_TOKEN` or the new `SERX_INTERNAL_BEARER_TOKEN`. JWT verification (EdDSA / auth-engine-x JWKS) is in the codebase and tested but is **not yet wired onto any route** — that cutover is Phase 3.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Auth dependencies in code](#2-auth-dependencies-in-code)
3. [Route auth posture](#3-route-auth-posture)
4. [Configuration](#4-configuration)
5. [JWT scaffolding (not yet wired)](#5-jwt-scaffolding-not-yet-wired)
6. [What is NOT in this system](#6-what-is-not-in-this-system)
7. [Usage examples](#7-usage-examples)
8. [Component map](#8-component-map)

---

## 1. Overview

The SERX API today uses bearer-token auth on internal and tenant-CRUD routes. There is no per-user login flow in the FastAPI service, no `/api/auth/login`, and no in-process `api_tokens` table lookups. The legacy multi-tenant scaffolding still exists in the database and in the dormant Next.js layer (`lib/auth.ts`), but is not on the request path.

After Phase 2, every authenticated route accepts **either** of two bearer secrets:

| Secret | Source | Status |
|---|---|---|
| `SERX_AUTH_TOKEN` | Legacy shared token | Still accepted; removed in Phase 3 |
| `SERX_INTERNAL_BEARER_TOKEN` | New canonical internal-caller bearer | Accepted; required at startup once Phase 1 lands |

Tenant context (`org_id`, `user_id`) on CRUD routes is still passed as **query parameters** by the caller. No DB enforcement of caller ↔ org entitlement; the bearer is fully trusted.

Public proposal routes (`/api/public/proposals/*`) remain anonymous. Cal.com and Stripe webhook routes use HMAC signature verification via `CAL_WEBHOOK_SECRET` and Stripe's webhook secret respectively — those paths are unchanged by Phase 1/2.

---

## 2. Auth dependencies in code

All FastAPI dependencies live in `app/auth/dependencies.py` and are re-exported from `app/auth/__init__.py`.

| Dependency | Purpose | Status |
|---|---|---|
| `verify_token_or_internal_bearer` | Token-only check; accepts legacy or new bearer | **Active** on internal routes |
| `get_current_org_or_internal_bearer` | Token + caller-supplied `org_id`/`user_id` query params; returns `AuthContext` | **Active** on tenant CRUD routes |
| `verify_token` | Legacy token-only (`SERX_AUTH_TOKEN` strictly) | Retained; not on any route |
| `get_current_org` | Legacy token + query params | Retained; aliased as `get_current_auth` |
| `require_internal_bearer` | Static `SERX_INTERNAL_BEARER_TOKEN` only; returns `InternalCallerContext` | Wired in Phase 3 |
| `get_current_auth_jwt` | EdDSA JWT verified via auth-engine-x JWKS | **Not yet wired**; Phase 3 |

### `AuthContext` (current shape)

```python
@dataclass
class AuthContext:
    org_id: str
    user_id: str
    role: str = ""
    auth_method: str = "shared_token"   # "shared_token" | "internal_bearer" | "session" | "m2m"
```

`auth_method` is set by whichever transitional dep authorized the call, which is useful for migration telemetry.

### `InternalCallerContext`

```python
@dataclass
class InternalCallerContext:
    caller: str = "internal"
```

Used by routes that authenticate non-interactive backend callers (serx-mcp, internal cron) without an org/user identity. Returned by `require_internal_bearer`. Today no routes consume it; in Phase 3 the internal routes that currently use `verify_token_or_internal_bearer` cut over to `require_internal_bearer`.

---

## 3. Route auth posture

| Router(s) | Dep used today | Notes |
|---|---|---|
| `internal.py`, `internal_cal_events.py`, `internal_meetings_deals.py`, `internal_scheduler.py`, `internal_webhook_events.py`, `orgs.py`, `users.py` | `verify_token_or_internal_bearer` | Token-only; no tenant scoping |
| `accounts.py`, `bank_details.py`, `clients.py`, `contacts.py`, `conversations.py`, `engagements.py`, `invoices.py`, `meetings.py`, `order_messages.py`, `order_tasks.py`, `orders.py`, `projects.py`, `proposals.py`, `services.py`, `tickets.py` | `get_current_org_or_internal_bearer` | Token + `org_id`/`user_id` query params |
| `public_proposals_router` (in `proposals.py`) | None | Public, anonymous |
| `cal_webhooks.py`, `calcom_webhooks.py`, Stripe webhook handler in `proposals.py` | HMAC signature verification | Unchanged by Phase 1/2 |
| `health.py` | None | Liveness |

---

## 4. Configuration

### Environment variables (current)

| Variable | Required | Purpose |
|---|---|---|
| `SERX_AUTH_TOKEN` | No (transitional) | Legacy shared bearer; still accepted in Phase 2, removed in Phase 3 |
| `SERX_INTERNAL_BEARER_TOKEN` | **Yes in production** | Canonical internal-caller bearer. Sourced from the shared-mcps Doppler config. Defaults to empty so dev/test boots, but auth deps return 503 when unset |
| `AUX_JWKS_URL` | Default provided | auth-engine-x JWKS endpoint; defaults to `https://api.authengine.dev/api/auth/jwks` |
| `AUX_ISSUER` | Default provided | JWT `iss` claim; defaults to `https://api.authengine.dev` |
| `AUX_AUDIENCE` | Default provided | JWT `aud` claim; defaults to `https://api.authengine.dev` |

`AUX_*` settings are read by the JWT scaffolding (`app/auth/jwt.py`) but no route enforces JWTs yet.

### Settings class

See `app/config.py`. Field comments call out the Phase 1/2 transitional state explicitly.

### Doppler

Both bearers and the `AUX_*` JWKS settings are sourced from Doppler. Do not commit token values to `.env` or any repo file.

---

## 5. JWT scaffolding (not yet wired)

Phase 1 added EdDSA JWT verification against the auth-engine-x JWKS endpoint:

- `app/auth/jwt.py` — `decode_access_token()` (session JWTs, `type=session`) and `decode_m2m_token()` (M2M JWTs, `type=m2m`). `PyJWKClient` caches signing keys for 5 minutes.
- `get_current_auth_jwt` in `app/auth/dependencies.py` — verifies a bearer JWT, checks `iss`/`aud`/`exp`, requires `sub`, and reconciles any `org_id` claim with the `org_id` query param. Session JWTs must additionally agree on `user_id`.

These are exported and unit-tested but **not attached to any route**. They become live in Phase 3 when CRUD routes cut over from `get_current_org_or_internal_bearer` to `get_current_auth_jwt`, and internal routes cut from `verify_token_or_internal_bearer` to `require_internal_bearer`.

---

## 6. What is NOT in this system

To prevent confusion with the prior version of this doc:

- There is **no** `/api/auth/login` endpoint in the FastAPI service.
- There is **no** `bcrypt` password verification on the request path.
- There is **no** `api_tokens` DB lookup on the request path.
- There is **no** `JWT_SECRET_KEY` / HS256 path. JWTs are EdDSA, JWKS-verified, externally issued by auth-engine-x.
- There is **no** schema or multi-tenant strip yet — the `users`, `org_members`, `api_tokens`, `roles` tables still exist in the database but are not consulted by SERX request handling.

---

## 7. Usage examples

### Internal caller (serx-mcp, OPEX, future Phase 3 cron)

```bash
curl -s "$SERX_API_BASE_URL/api/internal/orgs" \
  -H "Authorization: Bearer $SERX_INTERNAL_BEARER_TOKEN"
```

In Phase 2, `$SERX_AUTH_TOKEN` is also accepted on the same routes.

### Tenant CRUD caller

```bash
curl -s "$SERX_API_BASE_URL/api/clients?org_id=$ORG_ID&user_id=$USER_ID" \
  -H "Authorization: Bearer $SERX_INTERNAL_BEARER_TOKEN"
```

In Phase 2, `$SERX_AUTH_TOKEN` is also accepted on the same routes.

### Public proposal viewing

```bash
curl -s "$SERX_API_BASE_URL/api/public/proposals/$PROPOSAL_ID"
```

No bearer required.

---

## 8. Component map

| Component | Location | Purpose |
|---|---|---|
| `app/auth/__init__.py` | Module exports | Public API for FastAPI dependencies |
| `app/auth/dependencies.py` | Auth dependencies | `verify_token`, `verify_token_or_internal_bearer`, `get_current_org`, `get_current_org_or_internal_bearer`, `require_internal_bearer`, `get_current_auth_jwt`, `AuthContext`, `InternalCallerContext` |
| `app/auth/jwt.py` | JWT verification | `decode_access_token`, `decode_m2m_token` (EdDSA, auth-engine-x JWKS) |
| `app/config.py` | Settings | `SERX_AUTH_TOKEN`, `SERX_INTERNAL_BEARER_TOKEN`, `AUX_JWKS_URL`, `AUX_ISSUER`, `AUX_AUDIENCE` |
| `app/main.py` | Router wiring | Mounts all routers; no global auth middleware |
| `docs/SERX_AUTH_REMEDIATION_PHASE_1_2.md` | Canonical Phase 1+2 record | Full state, what's done, what's not, Phase 3 prerequisites |
