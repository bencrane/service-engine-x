Updated: Saturday, April 25, 2026 at 7:14 PM EDT

# SERX Auth Remediation — Phase 1 + Phase 2 (Canonical State)

This is the canonical record of the auth remediation work delivered for `service-engine-x` (SERX) through Phase 2. It captures exactly what shipped, what is intentionally still in place, what has not been done, and what must happen before Phase 3 can resume.

This file is authoritative. Older docs (`service-engine-x-api/docs/AUTHENTICATION.md`, `service-engine-x-api/docs/MULTI-TENANT-ARCHITECTURE.md`, `SERX_MIGRATION_AUDIT.md` Section 7) point here for the post-remediation state.

---

## 1. Scope

The remediation collapses SERX from a single-shared-bearer (`SERX_AUTH_TOKEN`) posture to a JWT-verified, JWKS-based auth model aligned with the auth-engine-x platform conventions. The work was sequenced into three phases:

- **Phase 1** — add JWT + internal-bearer scaffolding to SERX without changing route behavior. (Shipped.)
- **Phase 2** — rewire all internal and tenant CRUD routes onto transitional auth dependencies that accept *either* `SERX_AUTH_TOKEN` or `SERX_INTERNAL_BEARER_TOKEN`. (Shipped.)
- **Phase 3** — cut routes over to JWT verification (CRUD) and the strict internal bearer (internal), drop the legacy shared token, retire transitional helpers, and (separately) revisit schema/multi-tenant strip. (Not started.)

This document covers Phase 1 + Phase 2 only.

---

## 2. Branches and PRs

| Phase | Branch | PR | Head SHA at time of writing |
|---|---|---|---|
| Phase 1 | `phase-1-jwt-foundation` | #23 | `4b541790fb41ffb1a7bb65af4439fa185b290036` |
| Phase 2 | `phase-2-caller-migration-support` | #24 | `909d0dcdf6b9a41773cbdd0a2dc146cdae932713` |

PR #24 is stacked on PR #23. PR #23 base is `main`; PR #24 base is `phase-1-jwt-foundation`. Both PRs are no-behavior-change with respect to currently deployed callers — every existing caller using `SERX_AUTH_TOKEN` continues to work unchanged.

Commits on the Phase 2 branch (in order):

1. `db2d4a3` — Add JWT + internal-bearer auth scaffolding (Phase 1).
2. `ee6cdfe` — Add transitional auth dependencies (Phase 2 helpers).
3. `909d0dc` — Wire routers onto transitional auth dependencies (Phase 2 cutover).

---

## 3. Current state — exactly what the API does today

### 3.1 Bearers accepted

Every authenticated route accepts **either**:

- `SERX_AUTH_TOKEN` — the legacy shared bearer (still valid through Phase 2).
- `SERX_INTERNAL_BEARER_TOKEN` — the new canonical internal-caller bearer.

Constant-time comparison (`hmac.compare_digest` / `secrets.compare_digest`) on both. 503 returned when neither is configured. 401 returned with distinct details for missing header, malformed header, or token mismatch.

### 3.2 Tenant context

On tenant CRUD routes, `org_id` and `user_id` are still **caller-supplied query parameters** that pass through into `AuthContext`. The bearer is fully trusted; no DB-level entitlement check has been added in Phase 1/2.

### 3.3 Public proposal routes

`/api/public/proposals/*` remain anonymous, by design. Phase 1/2 did not touch this surface.

### 3.4 Webhook signature verification

- Cal.com webhooks (`/api/webhooks/cal`) — HMAC against `CAL_WEBHOOK_SECRET`. Unchanged.
- Cal.com raw sink (`/api/webhooks/calcom`) — no signature, immutable forensic capture. Unchanged.
- Stripe webhook handler in `proposals.py` — Stripe webhook secret signature verification. Unchanged.

### 3.5 JWT verification (scaffolded, not wired)

- EdDSA verification against the auth-engine-x JWKS endpoint via `PyJWKClient` with a 5-minute key cache.
- `decode_access_token()` validates `type=session`; `decode_m2m_token()` validates `type=m2m`. Both require `iss`, `aud`, `exp`, `sub`.
- `get_current_auth_jwt` is exported and unit-tested but **not attached to any route**.

### 3.6 Internal bearer dependency (scaffolded, not wired strictly)

- `require_internal_bearer` returns an `InternalCallerContext` (no org/user) and is exported.
- Phase 2 internal routes still use the *transitional* `verify_token_or_internal_bearer` (accepts both legacy and new), not `require_internal_bearer`. Strict cutover happens in Phase 3.

---

## 4. Files and components changed by Phase 1 / Phase 2

### Phase 1 — `db2d4a3` "Add JWT + internal-bearer auth scaffolding"

| File | Change |
|---|---|
| `service-engine-x-api/app/auth/__init__.py` | Export new symbols |
| `service-engine-x-api/app/auth/dependencies.py` | Add `InternalCallerContext`, `require_internal_bearer`, `get_current_auth_jwt`, `_extract_bearer_token` helper; extend `AuthContext` with `role` / `auth_method` |
| `service-engine-x-api/app/auth/jwt.py` | New: EdDSA JWKS verification (`decode_access_token`, `decode_m2m_token`) |
| `service-engine-x-api/app/config.py` | Add `SERX_INTERNAL_BEARER_TOKEN`, `AUX_JWKS_URL`, `AUX_ISSUER`, `AUX_AUDIENCE` |
| `service-engine-x-api/pyproject.toml` | Add `PyJWT[crypto]>=2.8.0` |
| `service-engine-x-api/tests/test_auth.py` | New: 10 unit tests covering internal-bearer dep and JWT dep |

No router files were touched in Phase 1. No deployed behavior changed.

### Phase 2 — `ee6cdfe` "Add transitional auth dependencies"

| File | Change |
|---|---|
| `service-engine-x-api/app/auth/dependencies.py` | Add `verify_token_or_internal_bearer`, `get_current_org_or_internal_bearer`, `_matches_legacy_token`, `_matches_internal_bearer` |
| `service-engine-x-api/app/auth/__init__.py` | Export the two new transitional deps |
| `service-engine-x-api/tests/test_auth_transitional.py` | New: 10 unit tests covering the transitional deps end-to-end |

### Phase 2 — `909d0dc` "Wire routers onto transitional auth dependencies"

22 router files updated to depend on the transitional helpers. No business logic or query bodies changed; only the auth dependency reference changed.

| Router | Replaced dep | New dep |
|---|---|---|
| `internal.py`, `internal_cal_events.py`, `internal_meetings_deals.py`, `internal_scheduler.py`, `internal_webhook_events.py`, `orgs.py`, `users.py` | `verify_token` | `verify_token_or_internal_bearer` |
| `accounts.py`, `bank_details.py`, `clients.py`, `contacts.py`, `conversations.py`, `engagements.py`, `invoices.py`, `meetings.py`, `order_messages.py`, `order_tasks.py`, `orders.py`, `projects.py`, `proposals.py`, `services.py`, `tickets.py` | `get_current_org` | `get_current_org_or_internal_bearer` |

`proposals.py` includes the public proposal sub-router; that sub-router was **not** changed (still anonymous).

---

## 5. Auth surface after Phase 2

| Route group | Auth dep | Bearers accepted | Tenant scoping |
|---|---|---|---|
| `/api/internal/**`, `/api/orgs`, `/api/users` | `verify_token_or_internal_bearer` | Legacy or new | Token-only (no org scoping) |
| `/api/clients`, `/api/services`, `/api/orders`, `/api/order-tasks`, `/api/order-messages`, `/api/proposals` (private), `/api/invoices`, `/api/tickets`, `/api/engagements`, `/api/projects`, `/api/conversations`, `/api/accounts`, `/api/contacts`, `/api/meetings`, `/api/bank-details` | `get_current_org_or_internal_bearer` | Legacy or new | Caller-supplied `org_id` / `user_id` query params |
| `/api/public/proposals/**` | None | n/a | n/a (anonymous) |
| `/api/webhooks/cal` | HMAC `CAL_WEBHOOK_SECRET` | n/a | n/a |
| `/api/webhooks/calcom` | None (raw sink) | n/a | n/a |
| Stripe webhook (in `proposals.py`) | Stripe signature | n/a | n/a |
| `/api/health` | None | n/a | n/a |

---

## 6. What has NOT been done

These items are intentionally out of scope for Phase 1 + Phase 2 and will be picked up in Phase 3 or later:

- No JWT cutover on any route. `get_current_auth_jwt` is exported but unwired.
- No strict internal-bearer cutover. Internal routes still use the dual-accepting transitional dep, not `require_internal_bearer`.
- `SERX_AUTH_TOKEN` is still a valid bearer everywhere it was before. Nothing has been removed.
- No DB-level org entitlement enforcement. `org_id` is still caller-supplied on CRUD routes.
- No schema strip. `users`, `org_members`, `api_tokens`, `roles` and related multi-tenant tables remain in the database, unused on the request path.
- No changes to the public proposal viewing/signing/payment routes.
- No changes to Cal.com or Stripe webhook signature verification logic.
- No changes to outbound auth (SERX → OPEX) — `OPEX_AUTH_TOKEN` is unchanged.
- No changes to serx-mcp, OPEX, auth-engine-x, outbound-engine-x, OEX, MAGS, or any sibling repo. Phase 1/2 was SERX-only.

---

## 7. Tests

Two test modules were added; both are unit tests against the FastAPI dependencies in isolation, using an inline FastAPI app fixture so no live database, JWKS server, or Doppler context is required.

### `service-engine-x-api/tests/test_auth.py` (Phase 1, 10 tests)

Covers `require_internal_bearer` and `get_current_auth_jwt`:

- `test_internal_bearer_missing_secret_returns_503`
- `test_internal_bearer_missing_header_returns_401`
- `test_internal_bearer_wrong_token_returns_401`
- `test_internal_bearer_correct_token_returns_200`
- `test_jwt_dep_missing_header_returns_401`
- `test_jwt_dep_invalid_token_returns_401`
- `test_jwt_dep_session_token_happy_path`
- `test_jwt_dep_session_user_id_mismatch_returns_403`
- `test_jwt_dep_m2m_token_org_mismatch_returns_403`
- `test_jwt_dep_m2m_token_happy_path`

### `service-engine-x-api/tests/test_auth_transitional.py` (Phase 2, 10 tests)

Covers `verify_token_or_internal_bearer` and `get_current_org_or_internal_bearer`:

- `test_verify_or_internal_no_secrets_returns_503`
- `test_verify_or_internal_accepts_legacy_token`
- `test_verify_or_internal_accepts_new_token`
- `test_verify_or_internal_rejects_unknown`
- `test_verify_or_internal_works_when_only_legacy_set`
- `test_verify_or_internal_works_when_only_new_set`
- `test_get_current_org_or_internal_legacy_path`
- `test_get_current_org_or_internal_new_path`
- `test_get_current_org_or_internal_rejects_unknown`
- `test_get_current_org_or_internal_requires_org_user`

Run locally with the project's existing test runner (`pytest` via `uv` per `pyproject.toml`).

---

## 8. Operator readiness sequence into Phase 3

The actual deployment-side caller reality differs from the original audit's read. SERX has **no direct Trigger.dev / Railway cron callers** into `/api/internal/scheduler/*` — those scheduled flows live in OPEX, and OPEX calls SERX. That changes the cutover order:

1. **Merge Phase 1 (PR #23).** Adds scaffolding, no behavior change.
2. **Merge Phase 2 (PR #24).** Routes accept both bearers. Existing OPEX callers still work with `SERX_AUTH_TOKEN`.
3. **Update OPEX Doppler.** Switch OPEX from sending `SERX_AUTH_TOKEN` to sending `SERX_INTERNAL_BEARER_TOKEN`. Verify in OPEX logs that scheduler dispatch and any other SERX-bound calls succeed against `/api/internal/**` and `/api/...` routes.
4. **Resume Phase 3 in SERX.** Cut routes over to JWT (CRUD) and `require_internal_bearer` (internal). Remove `SERX_AUTH_TOKEN` from settings and tests. Drop transitional helpers.
5. **Update serx-mcp last.** Brief breakage is acceptable because it is currently unused. Update its outbound bearer to `SERX_INTERNAL_BEARER_TOKEN` (or to a JWT issuer flow) after the Phase 3 cutover lands.

Items 1, 2 are inside this repository and are what this docs update reflects. Items 3, 4, 5 require coordination with OPEX and serx-mcp and are explicitly not in scope of Phase 1/2.

---

## 9. Doppler / environment requirements

| Variable | Phase 1 | Phase 2 | Phase 3 (planned) |
|---|---|---|---|
| `SERX_AUTH_TOKEN` | Present | Present (still accepted) | **Removed** |
| `SERX_INTERNAL_BEARER_TOKEN` | Present (required) | Present (required) | Present (required, sole internal bearer) |
| `AUX_JWKS_URL` | Default OK | Default OK | Default OK / pin to prod |
| `AUX_ISSUER` | Default OK | Default OK | Pin to prod issuer |
| `AUX_AUDIENCE` | Default OK | Default OK | Pin to prod audience |

Notes:

- `SERX_INTERNAL_BEARER_TOKEN` is sourced from the shared-mcps Doppler config so SERX, serx-mcp, and OPEX all reference the same secret.
- Both bearers default to empty in `Settings`; that lets local dev/tests boot, but `_check_token`, `require_internal_bearer`, and the transitional deps return **503** when their required secret is unset, so production cannot silently pass auth on a missing config.
- Do **not** commit any token values to `.env`, `.env.example`, or any repo file. Operator-facing token values live in Doppler only.

---

## 10. Phase 3 resume prerequisites

Before starting Phase 3 (in SERX), confirm:

1. PR #23 (`phase-1-jwt-foundation`) is merged into `main`.
2. PR #24 (`phase-2-caller-migration-support`) is merged into `main`.
3. OPEX Doppler has been updated to send `SERX_INTERNAL_BEARER_TOKEN` instead of `SERX_AUTH_TOKEN` against SERX, and OPEX → SERX traffic has been observed succeeding with the new bearer (look for `auth_method="internal_bearer"` in any future telemetry, or simply 2xx in OPEX logs against SERX scheduler/internal endpoints).
4. No other live caller is still relying on `SERX_AUTH_TOKEN` against SERX. (serx-mcp can remain on it through Phase 3 cutover; brief breakage there is acceptable.)
5. A decision is logged on JWT issuance for SERX-internal callers: do internal callers move to M2M JWTs from auth-engine-x, or stay on the static `SERX_INTERNAL_BEARER_TOKEN` indefinitely? Phase 3 wires `require_internal_bearer` regardless; the JWT-or-static decision affects Phase 4+.

When all prerequisites hold, Phase 3 can:

- Replace `get_current_org_or_internal_bearer` with `get_current_auth_jwt` on every CRUD router.
- Replace `verify_token_or_internal_bearer` with `require_internal_bearer` on every internal router.
- Remove `SERX_AUTH_TOKEN` from `app/config.py`, `verify_token`, `get_current_org`, and the transitional helpers.
- Delete `verify_token_or_internal_bearer`, `get_current_org_or_internal_bearer`, and the legacy `verify_token` / `get_current_org` deps once unreferenced.
- Update `tests/test_auth_transitional.py` accordingly (remove or fold into `test_auth.py`).

The schema strip (dropping the dormant `users` / `org_members` / `api_tokens` / `roles` tables) is a separate effort and should not be bundled with the Phase 3 auth cutover.
