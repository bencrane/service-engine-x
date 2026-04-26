Updated: Sunday, April 26, 2026

# Authentication Guide

This document describes the authentication system used by the Service Engine X (SERX) API after the AUX M2M JWT hard cutover.

For the cross-backend rollout context (which AUX backends have migrated, in what order, with what shape), see [`auth-engine-x/docs/AUX_M2M_MIGRATION_STATUS.md`](https://github.com/bencrane/auth-engine-x).

> **Status:** post-cutover. SERX trusts JWTs verified against the shared auth-engine-x JWKS via the `aux_m2m_server` library. The legacy `SERX_AUTH_TOKEN` and `SERX_INTERNAL_BEARER_TOKEN` static bearers have been removed.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Auth dependencies in code](#2-auth-dependencies-in-code)
3. [Route auth posture](#3-route-auth-posture)
4. [Configuration](#4-configuration)
5. [Outbound M2M (SERX → OPEX)](#5-outbound-m2m-serx--opex)
6. [What is NOT in this system](#6-what-is-not-in-this-system)
7. [Usage examples](#7-usage-examples)
8. [Component map](#8-component-map)

---

## 1. Overview

Every authenticated SERX route accepts a single bearer JWT, verified against the auth-engine-x JWKS by `aux_m2m_server.JWKSVerifier`. Two token shapes are accepted:

| Token type | `type` claim | Issued to | Notes |
|---|---|---|---|
| Session | `session` | HQ-frontend operator | Carries `sub` (user_id), `org_id`, `role` |
| System-actor M2M | `m2m` (with `actor_type=system_service`) | Sibling backends and MCPs (`serx-mcp`, OPEX scheduler, etc.) | Org-agnostic |

Org-scoped M2M (`actor_type=org_service`) is **not** accepted on any SERX route — SERX has no org-scoped machine callers today.

Tenant context (`org_id`, `user_id`) on CRUD routes is still passed as **query parameters** by the caller. For session tokens those query params are cross-checked against the JWT's `org_id` / `sub` claims (403 on mismatch). For system-M2M tokens the query params are accepted as caller-supplied request scope; the bearer is fully trusted.

Public proposal routes (`/api/public/proposals/*`) remain anonymous. Cal.com and Stripe webhook routes use HMAC signature verification via `CAL_WEBHOOK_SECRET` and Stripe's webhook secret respectively — those paths are unchanged.

---

## 2. Auth dependencies in code

All FastAPI dependencies live in `app/auth/dependencies.py` and are re-exported from `app/auth/__init__.py`. Token verification is delegated to `aux_m2m_server.get_verifier()`.

| Dependency | Purpose |
|---|---|
| `verify_token` | No-org dep used by `/api/internal/**`, `/api/orgs`, `/api/users`. Verifies bearer and returns `None`. |
| `get_current_org` | Tenant-CRUD dep. Verifies bearer and reads `org_id` / `user_id` query params. Returns `AuthContext`. Aliased as `get_current_auth` for routers that historically imported that name. |

### `AuthContext`

```python
@dataclass
class AuthContext:
    org_id: str | None
    user_id: str | None
    role: str = ""
    auth_method: str = "session"  # "session" | "system_m2m"
```

`auth_method` reflects which token shape authorized the call. For system-M2M callers `role` is synthesized as `"org_admin"`.

### Sentinel

`INTERNAL_CALLER_USER_ID = "00000000-0000-0000-0000-000000000000"` is exported for any historical consumers that compared against the old internal-caller user_id; kept stable across the cutover.

---

## 3. Route auth posture

| Router(s) | Dep used | Notes |
|---|---|---|
| `internal.py`, `internal_cal_events.py`, `internal_meetings_deals.py`, `internal_scheduler.py`, `internal_webhook_events.py`, `orgs.py`, `users.py` | `verify_token` | Token-only; no tenant scoping |
| `accounts.py`, `bank_details.py`, `clients.py`, `contacts.py`, `conversations.py`, `engagements.py`, `invoices.py`, `meetings.py`, `order_messages.py`, `order_tasks.py`, `orders.py`, `projects.py`, `proposals.py`, `services.py`, `tickets.py` | `get_current_org` (a.k.a. `get_current_auth`) | Token + `org_id` / `user_id` query params |
| `public_proposals_router` (in `proposals.py`) | None | Public, anonymous |
| `cal_webhooks.py`, `calcom_webhooks.py`, Stripe webhook handler in `proposals.py` | HMAC signature verification | Unchanged by the JWT cutover |
| `health.py` | None | Liveness |

---

## 4. Configuration

### Environment variables

All `AUX_*` variables are inherited from `aux_m2m_server.BaseAuthSettings` — do not redeclare them in `app/config.py`. They're owned upstream so every AUX backend uses identical field names and the same boot-required contract.

| Variable | Required | Purpose |
|---|---|---|
| `AUX_JWKS_URL` | **Yes** | auth-engine-x JWKS endpoint. JWKSVerifier fetches and caches signing keys from here. |
| `AUX_ISSUER` | **Yes** | Expected JWT `iss` claim. |
| `AUX_AUDIENCE` | **Yes** | Expected JWT `aud` claim. |
| `AUX_API_BASE_URL` | **Yes** | auth-engine-x base URL (used by the outbound `aux_m2m_client` token client). |
| `AUX_M2M_API_KEY` | **Yes** | SERX's per-backend M2M API key (sub `service:serx`). Used by the outbound token client to mint JWTs for calls to OPEX. **Never share this key across backends.** |

Settings class: `app/config.py` extends `BaseAuthSettings`. SERX-specific fields (Supabase, scheduler windows, third-party keys) live alongside the inherited AUX foundation.

### Doppler

`AUX_*` values are sourced from Doppler. Do not commit token values to `.env` or any repo file.

---

## 5. Outbound M2M (SERX → OPEX)

`app/routers/internal_scheduler.py` calls the managed-agents API at `OPEX_API_URL/events/receive`. Outbound auth uses `aux_m2m_client.AsyncM2MAuth` wrapping a lazily-constructed `AsyncM2MTokenClient(settings.to_m2m_config())`. The client mints / refreshes / caches JWTs automatically; there is no static `OPEX_AUTH_TOKEN` anymore.

```python
from aux_m2m_client import AsyncM2MAuth, AsyncM2MTokenClient
...
async with httpx.AsyncClient(auth=_get_opex_auth()) as client:
    response = await client.post(f"{settings.OPEX_API_URL}/events/receive", ...)
```

---

## 6. What is NOT in this system

- There is **no** `/api/auth/login` endpoint in the FastAPI service.
- There is **no** `bcrypt` password verification on the request path.
- There is **no** `api_tokens` DB lookup on the request path.
- There is **no** `JWT_SECRET_KEY` / HS256 path. JWTs are EdDSA, JWKS-verified, externally issued by auth-engine-x.
- There is **no** `SERX_AUTH_TOKEN` or `SERX_INTERNAL_BEARER_TOKEN` static bearer. Both were removed in the cutover.
- There is **no** `OPEX_AUTH_TOKEN` static bearer for outbound calls. Replaced by `aux_m2m_client.AsyncM2MAuth`.
- There is **no** local JWT decode logic. All verification flows through `aux_m2m_server.JWKSVerifier`.

---

## 7. Usage examples

### Internal caller (serx-mcp, OPEX, internal cron)

The caller (a sibling backend or MCP) mints a system-actor M2M JWT via `aux_m2m_client.AsyncM2MAuth` and presents it as `Authorization: Bearer <jwt>`:

```bash
curl -s "$SERX_API_BASE_URL/api/internal/orgs" \
  -H "Authorization: Bearer $SYSTEM_M2M_JWT"
```

### Tenant CRUD caller

Session JWT (HQ frontend) — `org_id` / `user_id` must match the JWT's `org_id` / `sub`:

```bash
curl -s "$SERX_API_BASE_URL/api/clients?org_id=$ORG_ID&user_id=$USER_ID" \
  -H "Authorization: Bearer $SESSION_JWT"
```

System-M2M JWT — `org_id` / `user_id` are caller-supplied scope:

```bash
curl -s "$SERX_API_BASE_URL/api/clients?org_id=$ORG_ID&user_id=$USER_ID" \
  -H "Authorization: Bearer $SYSTEM_M2M_JWT"
```

### Public proposal viewing

```bash
curl -s "$SERX_API_BASE_URL/api/public/proposals/$PROPOSAL_ID"
```

No bearer required.

---

## 8. Component map

| Component | Location | Purpose |
|---|---|---|
| `app/auth/__init__.py` | Module exports | `AuthContext`, `INTERNAL_CALLER_USER_ID`, `verify_token`, `get_current_org`, `get_current_auth` |
| `app/auth/dependencies.py` | Auth dependencies | `verify_token`, `get_current_org` (alias `get_current_auth`), `AuthContext`, internal helpers `_extract_bearer_token` / `_verify` / `_verify_session_or_system_m2m` |
| `app/config.py` | Settings | Extends `aux_m2m_server.BaseAuthSettings`; SERX-specific fields only |
| `app/main.py` | App bootstrap | Wires `set_verifier(JWKSVerifier(settings.to_auth_settings()))` at import time, before any FastAPI dep resolves |
| `app/routers/internal_scheduler.py` | Outbound M2M | Uses `aux_m2m_client.AsyncM2MAuth` for SERX → OPEX dispatch |
| `tests/test_auth.py` | Unit tests | Patches `app.auth.dependencies._verify` to exercise both deps without a live JWKS endpoint |
