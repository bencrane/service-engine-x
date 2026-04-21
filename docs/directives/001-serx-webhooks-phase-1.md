# Directive 1: Build `serx-webhooks` Phase 1 — Dumb Cal.com Webhook Ingestion

**Context:** You are working on the `service-engine-x` monorepo at `/Users/benjamincrane/service-engine-x`. Read `CLAUDE.md` (repo root) before starting if present.

**Scope clarification on autonomy:** You are a senior engineer. Within the scope below, make strong decisions. What you must not do is drift outside scope, modify sibling folders, create Railway apps, create git branches, set up Doppler projects, or run deploy commands. If you discover a hard-constraint tension, stop and surface it in the completion report rather than silently working around it.

**Background:** The previous Cal.com webhook handler lives in `service-engine-x-api/app/routers/cal_webhooks.py` and has repeatedly failed in production. The most recent failure: a Pipedream workflow assumed Cal.com's `MEETING_STARTED` body contained a nested `.payload` key, but Cal.com sends `MEETING_STARTED` and `MEETING_ENDED` in a **flat** envelope (booking fields at the top level, no `payload` wrapper) — violating a `NOT NULL` constraint. Rather than patch, the owner wants a brand-new, isolated, dumb-and-reliable ingestion service deployed as a **separate Railway app** on its own branch (`webhooks-prod`). Phase 1 scope is deliberately minimal: receive the webhook, return `202 Accepted` immediately, store the full body in a fresh table. No user/org lookup, no routing table, no managed-agent dispatch — those are future phases.

---

## Hard Constraints (not up for debate)

1. **Runtime platform: Railway.** New, separate Railway app — not a second service in the existing `service-engine-x-api` Railway project. Executor does **not** create the Railway app.
2. **Same repo (`service-engine-x`), different deploy branch.** Target branch is `webhooks-prod`. Executor does **not** create this branch; commits land on whatever branch the executor is working on and the owner merges.
3. **Framework: FastAPI. Language: Python 3.12.** Mirror the shape of the existing `service-engine-x-api/` sibling folder.
4. **Secrets: Doppler only.** Railway will carry only `DOPPLER_TOKEN`. Dockerfile installs the Doppler CLI and wraps uvicorn with `doppler run --`. Executor does **not** set up Doppler; just make the app Doppler-compatible. All env vars come from Doppler at runtime — never from bare shell variables.
5. **Storage: shared Supabase.** Writes to a **new** table, `webhook_events_raw`. Do **not** reuse or reference the existing `cal_webhook_events_raw` or `cal_raw_events` tables in `service-engine-x-api`. Do **not** run the migration against any DB — the owner will.
6. **Decoupling discipline.** `serx-webhooks/` must not import from `service-engine-x-api/`, `service-engine-x-mcp/`, or any sibling folder. Greenfield code only. (No CI import-boundary check required in phase 1 — the folder has nothing to import from yet.)
7. **Leave `service-engine-x-api/app/routers/cal_webhooks.py` alone.** No diff against that file. No deletions, no refactors, no comments.

---

## Existing code to read before starting

- `service-engine-x-api/Dockerfile` — copy the Doppler CLI install block and the `doppler run --` CMD exactly. This is the deployment contract.
- `service-engine-x-api/railway.toml` — copy the shape; only `healthcheckPath` changes.
- `service-engine-x-api/pyproject.toml` — reference for `[build-system]`, `[tool.setuptools.packages.find]`, `[tool.ruff]`. Your `pyproject.toml` is a slimmer subset.
- `service-engine-x-api/app/main.py` — reference for FastAPI init pattern. Skip the custom validation exception handler; you don't need it.
- `service-engine-x-api/app/config.py` — reference for `pydantic-settings`. Note: existing code uses `SERVICE_ENGINE_X_SUPABASE_*` prefixed vars; **your new app uses plain `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY`** (fresh Doppler config, clean names).
- `service-engine-x-api/app/database.py` — copy the `@lru_cache` supabase client factory pattern, adjusted for new env names.
- `service-engine-x-api/app/routers/health.py` — reference for health endpoint shape.
- `service-engine-x-api/app/routers/cal_webhooks.py` — **reference only for the `_verify_signature` HMAC-SHA256 pattern (lines ~28–48)**. Do not copy the store/route/projection logic. Phase 1 is dumber than this file.
- `/Users/benjamincrane/api-reference-docs-new/cal.com/` — skim only if you need to confirm the header name (`X-Cal-Signature-256`) or that `triggerEvent` is at the top level in **both** flat and nested shapes. It is.

---

## Build 1: Project scaffolding

### `serx-webhooks/Dockerfile` (new)

Mirror `service-engine-x-api/Dockerfile` exactly: `python:3.12-slim`, Doppler CLI install block, `COPY pyproject.toml .`, `pip install --no-cache-dir .`, `COPY . .`, `EXPOSE 8000`, and:

```
CMD ["sh", "-c", "doppler run -- uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

### `serx-webhooks/railway.toml` (new)

```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/health/live"
healthcheckTimeout = 30
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
```

### `serx-webhooks/pyproject.toml` (new)

```toml
[project]
name = "serx-webhooks"
version = "0.1.0"
description = "Service Engine X — webhook ingestion service"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115,<1",
    "uvicorn[standard]>=0.34,<1",
    "pydantic>=2.7,<3",
    "pydantic-settings>=2.7,<3",
    "supabase>=2.13,<3",
]

[project.optional-dependencies]
dev = [
    "pytest>=8,<9",
    "httpx>=0.28,<1",
    "ruff>=0.9,<1",
]

[tool.setuptools.packages.find]
include = ["app*"]

[build-system]
requires = ["setuptools>=75"]
build-backend = "setuptools.build_meta"

[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
```

### `serx-webhooks/.dockerignore` (new)

```
__pycache__/
*.pyc
*.pyo
.venv/
venv/
.env
.env.*
.git/
.gitignore
tests/
.pytest_cache/
.ruff_cache/
*.md
```

---

## Build 2: Migration

**File:** `serx-webhooks/migrations/001_webhook_events_raw.sql` (new)

```sql
create table if not exists webhook_events_raw (
    id uuid primary key default gen_random_uuid(),
    source text not null,
    trigger_event text,
    event_key text not null,
    payload jsonb not null,
    raw_body bytea not null,
    headers jsonb,
    signature_valid boolean,
    status text not null default 'received'
        check (status in ('received', 'processed', 'failed', 'dead_letter')),
    received_at timestamptz not null default now(),
    constraint webhook_events_raw_source_event_key_unique
        unique (source, event_key)
);

create index if not exists webhook_events_raw_source_event_received_idx
    on webhook_events_raw (source, trigger_event, received_at desc);

create index if not exists webhook_events_raw_status_received_idx
    on webhook_events_raw (status, received_at desc);
```

Rationale for fields:
- `event_key` + unique constraint → idempotency. Cal.com redelivery or double-hop delivery collapses to one row.
- `raw_body bytea` → lossless storage of the exact bytes Cal.com sent. Useful for HMAC re-verification or parse debugging.
- `payload jsonb` → parsed body, or `{"_raw_text": "..."}` wrapper when parse fails.
- `status` with default `'received'` → lifecycle column so phase 2 can transition rows without a schema migration.
- `signature_valid` nullable → `true`/`false` when `CAL_WEBHOOK_SECRET` is set, `null` when it isn't.

---

## Build 3: Configuration

**File:** `serx-webhooks/app/config.py` (new)

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Supabase (Doppler-injected)
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Cal.com webhook HMAC — empty means skip verification and log warning
    CAL_WEBHOOK_SECRET: str = ""

    # Runtime
    PORT: int = 8000
    DEBUG: bool = False
    APP_NAME: str = "serx-webhooks"
    APP_VERSION: str = "0.1.0"

    # CORS — permissive for phase 1
    CORS_ORIGINS: list[str] = ["*"]


settings = Settings()  # type: ignore[call-arg]
```

---

## Build 4: Database client

**File:** `serx-webhooks/app/database.py` (new)

```python
"""Supabase client initialization."""

from functools import lru_cache

from supabase import Client, create_client

from app.config import settings


@lru_cache
def get_supabase() -> Client:
    """Get cached Supabase client instance."""
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY,
    )
```

---

## Build 5: Health router

**File:** `serx-webhooks/app/routers/health.py` (new)

```python
"""Health endpoints. /health/live is static; /health/ready pings Supabase."""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.database import get_supabase

logger = logging.getLogger("serx_webhooks.health")

router = APIRouter(tags=["Health"])


@router.get("/health/live")
async def liveness() -> dict:
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness() -> JSONResponse:
    try:
        get_supabase().table("webhook_events_raw").select("id", head=True, count="exact").limit(1).execute()
        return JSONResponse(status_code=200, content={"status": "ok"})
    except Exception as exc:
        logger.exception("readiness check failed")
        return JSONResponse(status_code=503, content={"status": "unavailable", "error": str(exc)})
```

---

## Build 6: Cal.com webhook router (the hot path)

**File:** `serx-webhooks/app/routers/cal.py` (new)

**Critical behavior:**
1. Return `202 Accepted` **immediately**, before any DB work or HMAC computation. Use FastAPI `BackgroundTasks`.
2. Background task: compute `event_key = sha256_hex(raw_body)`, decode body, attempt JSON parse, compute HMAC validity, insert row. Any exception is logged and swallowed — the client already got 202.
3. `payload` is NOT NULL. Non-JSON bodies → `{"_raw_text": "<utf-8 decoded with replacement>"}`.
4. `trigger_event`: `parsed.get("triggerEvent")` if `parsed` is a dict, else `None`. Top level in both Cal.com shapes.
5. HMAC: empty secret → log warning, `signature_valid=None`. Secret set, header missing → `False`. Otherwise `hmac.compare_digest(expected, header)`.
6. Headers stored as `{k.lower(): v for k, v in request.headers.items()}`.
7. `source = "cal.com"` hardcoded.
8. Idempotency: insert with `source` + `event_key`. On `unique_violation` (Postgres `23505`), catch, log `duplicate=true`, do not re-raise.
9. Structured log line per request, fields: `event=webhook_stored` (or `webhook_duplicate`, `webhook_error`), `source`, `trigger_event`, `event_key`, `row_id`, `signature_valid`, `duplicate`, `latency_ms`.

```python
import hashlib
import hmac
import json
import logging
import time
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import get_supabase

logger = logging.getLogger("serx_webhooks.cal")

router = APIRouter(tags=["Cal.com Webhooks"])


def _compute_signature_valid(raw_body: bytes, signature_header: str | None) -> bool | None:
    secret = settings.CAL_WEBHOOK_SECRET
    if not secret:
        logger.warning("CAL_WEBHOOK_SECRET not set — signature_valid stored as null")
        return None
    if not signature_header:
        return False
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def _parse_payload(raw_body: bytes) -> tuple[Any, str | None]:
    """Return (payload_for_jsonb, trigger_event_or_none)."""
    try:
        parsed = json.loads(raw_body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {"_raw_text": raw_body.decode("utf-8", errors="replace")}, None
    trigger_event = parsed.get("triggerEvent") if isinstance(parsed, dict) else None
    return parsed, trigger_event


def _store_event(
    raw_body: bytes,
    headers: dict[str, str],
    signature_header: str | None,
    t_start: float,
) -> None:
    """Background task: parse + insert. Never raises."""
    event_key = hashlib.sha256(raw_body).hexdigest()
    trigger_event = None
    row_id = None
    duplicate = False
    signature_valid: bool | None = None

    try:
        payload, trigger_event = _parse_payload(raw_body)
        signature_valid = _compute_signature_valid(raw_body, signature_header)
        row = {
            "source": "cal.com",
            "trigger_event": trigger_event,
            "event_key": event_key,
            "payload": payload,
            "raw_body": raw_body.decode("latin-1"),
            "headers": headers,
            "signature_valid": signature_valid,
        }
        result = get_supabase().table("webhook_events_raw").insert(row).execute()
        row_id = result.data[0].get("id") if result.data else None
    except Exception as exc:
        msg = str(exc)
        if "23505" in msg or "duplicate key" in msg.lower():
            duplicate = True
        else:
            logger.exception(
                "webhook_error source=cal.com trigger_event=%s event_key=%s",
                trigger_event,
                event_key,
            )
            return

    latency_ms = int((time.monotonic() - t_start) * 1000)
    logger.info(
        "%s source=cal.com trigger_event=%s event_key=%s row_id=%s signature_valid=%s duplicate=%s latency_ms=%d",
        "webhook_duplicate" if duplicate else "webhook_stored",
        trigger_event,
        event_key,
        row_id,
        signature_valid,
        duplicate,
        latency_ms,
    )


@router.post("/webhooks/cal")
async def cal_webhook(request: Request, background_tasks: BackgroundTasks) -> JSONResponse:
    t_start = time.monotonic()
    raw_body = await request.body()
    headers = {k.lower(): v for k, v in request.headers.items()}
    signature_header = request.headers.get("X-Cal-Signature-256")
    background_tasks.add_task(_store_event, raw_body, headers, signature_header, t_start)
    return JSONResponse(status_code=202, content={"status": "accepted"})
```

**Note on `raw_body` column:** supabase-py inserts go through PostgREST as JSON, which doesn't natively serialize `bytes`. `raw_body.decode("latin-1")` is a lossless round-trip (latin-1 covers all 256 byte values), and the column is `bytea`. If this approach fails in testing, the executor may substitute: (a) base64-encode into a `text` column renamed `raw_body_b64`, (b) drop the `raw_body` column entirely and rely on the `payload` JSONB + `{"_raw_text": ...}` fallback. Document the chosen approach in the completion report.

---

## Build 7: App entrypoint

**File:** `serx-webhooks/app/main.py` (new)

```python
"""FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.cal import router as cal_router
from app.routers.health import router as health_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Service Engine X — webhook ingestion service",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(cal_router)
```

**File:** `serx-webhooks/app/__init__.py` (new, empty)
**File:** `serx-webhooks/app/routers/__init__.py` (new, empty)

---

## Build 8: Smoke test (optional)

**File:** `serx-webhooks/tests/test_webhook_smoke.py` (new, optional)

If added, cover:
- `POST /webhooks/cal` with nested `BOOKING_CREATED` body → 202 + `{"status":"accepted"}`
- `POST /webhooks/cal` with flat `MEETING_STARTED` body → 202 + `{"status":"accepted"}`
- `POST /webhooks/cal` with non-JSON body → 202 + `{"status":"accepted"}`
- After background-task flush: fake supabase client recorded rows with full body under `payload` for JSON cases, `{"_raw_text": ...}` for non-JSON, `trigger_event` correct for the two shapes, `None` for non-JSON.
- Duplicate POST (same body twice) → second insert triggers unique-violation path; log contains `duplicate=true`.
- `GET /health/live` → 200
- `GET /health/ready` with fake Supabase failing → 503

Skip if it turns into a rabbit hole.

---

## What NOT to do

- Do **not** create Railway apps, create the `webhooks-prod` branch, set up Doppler projects, touch `DOPPLER_TOKEN`, or deploy.
- Do **not** modify anything in `service-engine-x-api/`, `service-engine-x-mcp/`, `cal-mcp/`, `app/` (Next.js root), or any other sibling folder. `git diff` against those paths must be empty.
- Do **not** touch existing `cal_webhook_events_raw` or `cal_raw_events` tables. Do not run the new migration against any DB.
- Do **not** add user lookup, organizer-email resolution, `org_id` resolution, route-table lookup, or managed-agent dispatch.
- Do **not** extract Cal.com payload fields beyond `triggerEvent`. No `uid`, `hosts`, `attendees`, `eventTypeId`.
- Do **not** gate the HTTP response on HMAC validity. Invalid signatures get stored with `signature_valid=false` and still return 202.
- Do **not** reject non-JSON bodies.
- Do **not** add rate limiting, body-size caps, or content-type enforcement.
- Do **not** verify locally by exporting bare shell env vars (e.g. `SUPABASE_URL=x python -c ...`). All env access goes through Doppler. If the executor lacks a Doppler config, verify via `docker build` + `docker run -e DOPPLER_TOKEN=<dev-token>` instead.
- Do **not** push commits or open a PR.
- Do **not** write a runbook, dashboard docs, or CI config. Phase 1 is stand-it-up only.

---

## Scope

Files to create:
- `serx-webhooks/Dockerfile`
- `serx-webhooks/railway.toml`
- `serx-webhooks/pyproject.toml`
- `serx-webhooks/.dockerignore`
- `serx-webhooks/migrations/001_webhook_events_raw.sql`
- `serx-webhooks/app/__init__.py`
- `serx-webhooks/app/main.py`
- `serx-webhooks/app/config.py`
- `serx-webhooks/app/database.py`
- `serx-webhooks/app/routers/__init__.py`
- `serx-webhooks/app/routers/health.py`
- `serx-webhooks/app/routers/cal.py`
- (optional) `serx-webhooks/tests/test_webhook_smoke.py`

Files to modify: **none**.

**One commit. Do not push.**

Commit message:

```
Scaffold serx-webhooks: isolated Cal.com webhook ingestion service

New top-level FastAPI app that receives Cal.com webhooks, returns 202
immediately, and persists the full body, raw bytes, headers, and HMAC
validity to a fresh webhook_events_raw table via a FastAPI
BackgroundTask. Idempotent via sha256(raw_body) unique key. Replaces
the failing handler in service-engine-x-api. Doppler-only secrets;
deploys as a separate Railway app on the webhooks-prod branch.
```

---

## When done

Report the following with evidence:

(a) Every file created, grouped by: app code, migration, deploy artifacts, tests (if any). Include line counts.

(b) Confirm `docker build -t serx-webhooks .` succeeds from inside `serx-webhooks/`. Paste the final image line.

(c) Confirm imports work the way production runs — via Doppler:

```
cd serx-webhooks && doppler run -- python -c "from app.main import app; [print(r.path) for r in app.routes]"
```

Expect `/health/live`, `/health/ready`, `/webhooks/cal` with no import errors. If no Doppler config is available to the executor, fall back to: `docker run --rm -e DOPPLER_TOKEN=<dev-token> serx-webhooks` and confirm the uvicorn startup logs show no `ValidationError`. Do not use bare shell env vars.

(d) Run the app (via Doppler or the Docker fallback above) against a throwaway Supabase (or a fake): POST a `BOOKING_CREATED`-shape body and a `MEETING_STARTED`-shape body to `/webhooks/cal`. Paste the `curl` output (expect 202 on both) and the resulting log lines (expect `webhook_stored`, correct `trigger_event` values). If you skipped this because no DB is available, explicitly say so.

(e) POST the same body twice. Confirm the second produces a log line with `duplicate=true` and still returns 202.

(f) Confirm `git diff -- service-engine-x-api/` is empty.

(g) Report the `raw_body` serialization approach you used (latin-1 decode, base64, or column-dropped) and why.

(h) Any deviations from this directive and the reasoning behind each.

(i) `git status` showing one staged commit and a clean working tree. Do not push.
