# serx-webhooks

Isolated, dumb-and-reliable webhook ingestion service for Service Engine X.
Phase 1: Cal.com webhooks only.

---

## What this service does

Receives Cal.com webhooks, returns `202 Accepted` immediately, and stores the
full body to Supabase via a FastAPI background task. Nothing else. No routing,
no user lookup, no agent dispatch — those live in future phases.

**Why it exists:** the previous handler at
`service-engine-x-api/app/routers/cal_webhooks.py` repeatedly failed in
production. Most recent failure: a Pipedream workflow assumed Cal.com's
`MEETING_STARTED` body contained a nested `.payload` key, but Cal.com sends
`MEETING_STARTED`/`MEETING_ENDED` in a **flat** envelope — violating a NOT NULL
constraint. Rather than patch a brittle system, we stood up a brand-new,
isolated service on its own Railway app, own branch, own table.

The old handler is untouched. Both services can coexist until Cal.com
webhooks are cut over to this endpoint.

---

## Current state (Phase 1 — LIVE)

- **Status:** deployed and verified in production
- **URL:** `https://serx-webhooks-ingest-production.up.railway.app`
- **Railway service:** `serx-webhooks-ingest`
- **Deploy branch:** `webhooks-prod`
- **Commit:** `c928c9a` — "Scaffold serx-webhooks: isolated Cal.com webhook ingestion service"
- **Health:** `/health/live` 200, `/health/ready` 200 (both verified against prod)
- **Test traffic received:** 3 rows in `webhook_events_raw` (nested, flat, non-JSON payloads; plus one duplicate that correctly collapsed on the unique key)

### What's NOT done yet (phase 2+)

- Cal.com is **not** yet pointed at this endpoint. The active production webhook is still the old `service-engine-x-api` handler. Cutover is a separate step (see "Cutover" section below).
- `CAL_WEBHOOK_SECRET` is unset in Doppler — all stored events have `signature_valid=null` by design until Cal.com is wired up with a real secret.
- No user/org resolution, no managed-agent dispatch, no route table — all phase 2+.

---

## Architecture

### Routes

| Method | Path                | Purpose                                                         |
|--------|---------------------|-----------------------------------------------------------------|
| GET    | `/health/live`      | Static liveness probe (Railway healthcheck target)              |
| GET    | `/health/ready`     | Reads `webhook_events_raw` via Supabase; 503 if DB unreachable  |
| POST   | `/webhooks/cal`     | Cal.com webhook ingestion                                       |

### Ingestion flow

```
Cal.com POST /webhooks/cal
  ├── read raw body
  ├── grab headers (lowercased) and X-Cal-Signature-256
  ├── schedule background task
  └── return 202 Accepted  ← client sees this immediately

BackgroundTask (never raises):
  ├── event_key = sha256(raw_body)
  ├── json.loads(raw_body)
  │     ├── success → payload = parsed, trigger_event = parsed.get("triggerEvent")
  │     └── failure → payload = {"_raw_text": "<utf-8 with replacement>"}, trigger_event = None
  ├── signature_valid = hmac-sha256(secret, raw_body) == header (None if no secret)
  ├── INSERT into webhook_events_raw
  │     └── on unique-violation (23505): log duplicate=true, do not re-raise
  └── structured log line (event, trigger_event, event_key, row_id, signature_valid, duplicate, latency_ms)
```

### Key design choices

- **202 immediately, then persist.** HMAC validity, JSON parsing, and DB insert all happen in the background. Cal.com never waits on our DB. Even if Supabase is down, we return 202 (the task logs the error and the event is lost — acceptable for phase 1 because Cal.com retries on non-2xx anyway; if we ever need at-least-once durability through Supabase outages, we add a local disk buffer in phase 2).
- **Idempotency via `sha256(raw_body)`.** Cal.com redelivery, Pipedream double-hop, or any accidental retry collapses to a single row. The unique constraint is `(source, event_key)`.
- **Non-JSON bodies are accepted, not rejected.** We store them with `payload = {"_raw_text": "..."}` and `trigger_event = null`. Phase 1 is "receive everything, lose nothing."
- **Invalid signatures don't gate the response.** Rows land with `signature_valid=false` and still return 202. Phase 2 can decide how to handle those (drop, quarantine, alert).
- **`raw_body` stored as `bytea`** with a latin-1 round-trip through supabase-py's JSON transport. Latin-1 is a lossless 1:1 mapping for all 256 byte values. If PostgREST ever rejects the implicit text→bytea cast (it hasn't in testing), the fallback options are (a) base64 into a text column, or (b) drop the `raw_body` column and rely on `payload.jsonb` alone.

### Storage: `webhook_events_raw`

Lives in the **shared** Supabase project (same as `service-engine-x-api`).
RLS is enabled; the service role key (used by this service) bypasses RLS by
design, so no policies are needed for our access path.

```sql
-- See serx-webhooks/migrations/001_webhook_events_raw.sql for the authoritative schema
create table webhook_events_raw (
    id uuid primary key default gen_random_uuid(),
    source text not null,                                      -- hardcoded "cal.com" in phase 1
    trigger_event text,                                        -- e.g. BOOKING_CREATED, MEETING_STARTED; null for non-JSON
    event_key text not null,                                   -- sha256(raw_body)
    payload jsonb not null,                                    -- parsed body, or {"_raw_text": "..."}
    raw_body bytea not null,                                   -- latin-1 round-trip of original bytes
    headers jsonb,                                             -- lowercase header map
    signature_valid boolean,                                   -- true/false if secret set; null otherwise
    status text not null default 'received'
        check (status in ('received', 'processed', 'failed', 'dead_letter')),
    received_at timestamptz not null default now(),
    unique (source, event_key)
);

-- Indexes
create index webhook_events_raw_source_event_received_idx
    on webhook_events_raw (source, trigger_event, received_at desc);
create index webhook_events_raw_status_received_idx
    on webhook_events_raw (status, received_at desc);
```

The `status` column exists so phase 2 can transition rows through the
pipeline (`received` → `processed` | `failed` | `dead_letter`) without a
schema migration.

**Do not confuse with** `cal_webhook_events_raw` or `cal_raw_events` — those
are the old tables used by `service-engine-x-api`. This service is
deliberately decoupled.

---

## Deployment

### Repo layout

```
service-engine-x/                          ← monorepo
├── app/                                   ← Next.js frontend (don't touch)
├── service-engine-x-api/                  ← old FastAPI (don't touch)
├── service-engine-x-mcp/                  ← MCP server (don't touch)
├── cal-mcp/                               ← (don't touch)
└── serx-webhooks/                         ← THIS SERVICE
    ├── Dockerfile                         ← python:3.12-slim + Doppler CLI + doppler run -- uvicorn
    ├── railway.toml                       ← healthcheck /health/live
    ├── pyproject.toml                     ← fastapi, uvicorn, pydantic-settings, supabase
    ├── .dockerignore
    ├── .gitignore
    ├── migrations/
    │   └── 001_webhook_events_raw.sql     ← already run in Supabase
    ├── app/
    │   ├── main.py                        ← FastAPI init + CORS + router wiring
    │   ├── config.py                      ← pydantic-settings; reads SUPABASE_*, CAL_WEBHOOK_SECRET
    │   ├── database.py                    ← @lru_cache supabase client factory
    │   └── routers/
    │       ├── health.py                  ← /health/live, /health/ready
    │       └── cal.py                     ← /webhooks/cal + HMAC + parse + background insert
    └── tests/
        └── test_webhook_smoke.py          ← 7 tests, all pass locally with monkeypatched supabase
```

### Git branches

- `main` — does not contain `serx-webhooks/`. This is by design: the service lives only on the deploy branch.
- `webhooks-prod` — the deploy branch. Railway watches this branch.
- When making changes: branch off `webhooks-prod`, PR back into `webhooks-prod`. Do **not** merge into `main` unless you have a reason to make the code cross-branch-visible.

### Railway

- **Project:** (owner-managed, not the same project as `service-engine-x-api`)
- **Service name:** `serx-webhooks-ingest`
- **Source Repo:** `bencrane/service-engine-x`
- **Branch:** `webhooks-prod`
- **Root Directory:** `/serx-webhooks`
- **Builder:** `Dockerfile` (NOT Railpack — Railpack auto-detects Node from the monorepo root and builds the Next.js app by mistake)
- **Dockerfile Path:** `/serx-webhooks/Dockerfile`
- **Healthcheck:** `/health/live` (30s timeout)
- **Restart policy:** `on_failure`, max 3 retries

### Doppler

Railway carries exactly one env var at the platform level: **`DOPPLER_TOKEN`**.
Everything else comes from the Doppler config bound to that token. The
Dockerfile CMD is `doppler run -- uvicorn ...` — uvicorn only sees env from
Doppler's injection.

**Required Doppler secrets:**

| Key                          | Required? | Notes                                                                   |
|------------------------------|-----------|-------------------------------------------------------------------------|
| `SUPABASE_URL`               | Yes       | Shared Supabase project URL                                             |
| `SUPABASE_SERVICE_ROLE_KEY`  | Yes       | Service role key (not anon) — needed for insert and to bypass RLS       |
| `CAL_WEBHOOK_SECRET`         | No (yet)  | Set when Cal.com is pointed at this endpoint. Empty = `signature_valid=null` on all rows. |

**Do NOT set in Doppler:**

- `PORT` — Railway injects it at the platform level; the Dockerfile reads `${PORT:-8000}` at shell time before `doppler run` executes.
- `DEBUG`, `APP_NAME`, `APP_VERSION`, `CORS_ORIGINS` — defaults in `app/config.py` are fine for phase 1. Only set if overriding.

### Exception: the `PORT` gotcha

The Dockerfile CMD is `sh -c "doppler run -- uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"`. `${PORT:-8000}` is expanded by the shell **before** `doppler run` starts, so it picks up Railway's platform-injected `PORT`, not a Doppler value. This is correct and desired — don't "fix" it.

---

## Verification / test recipes

### Health

```bash
URL=https://serx-webhooks-ingest-production.up.railway.app
curl -i "$URL/health/live"          # 200 {"status":"ok"}
curl -i "$URL/health/ready"         # 200 {"status":"ok"} — hits Supabase
```

### End-to-end POST sweep (synthetic traffic)

```bash
URL=https://serx-webhooks-ingest-production.up.railway.app

# Nested shape (BOOKING_* events — have a .payload wrapper)
curl -s -X POST "$URL/webhooks/cal" -H 'content-type: application/json' \
  -d '{"triggerEvent":"BOOKING_CREATED","createdAt":"2026-04-21T00:00:00Z","payload":{"uid":"test-1"}}'

# Flat shape (MEETING_* events — booking fields at top level, no wrapper)
curl -s -X POST "$URL/webhooks/cal" -H 'content-type: application/json' \
  -d '{"triggerEvent":"MEETING_STARTED","bookingId":999,"roomName":"test-room"}'

# Non-JSON (defensive)
curl -s -X POST "$URL/webhooks/cal" -H 'content-type: text/plain' \
  --data-binary 'not-json-at-all'

# Duplicate (same body twice — second collapses via unique key)
curl -s -X POST "$URL/webhooks/cal" -H 'content-type: application/json' \
  -d '{"triggerEvent":"BOOKING_CREATED","createdAt":"2026-04-21T00:00:00Z","payload":{"uid":"test-1"}}'
```

All four should return `202 {"status":"accepted"}`. Railway logs show three
`webhook_stored ...` lines and one `webhook_duplicate ... duplicate=True`.

### Inspect in Supabase

```sql
select id, trigger_event, signature_valid, status, received_at,
       jsonb_path_query_first(payload, '$.payload.uid')   as nested_uid,
       jsonb_path_query_first(payload, '$.bookingId')     as flat_booking_id,
       jsonb_path_query_first(payload, '$._raw_text')     as raw_text
from webhook_events_raw
order by received_at desc
limit 10;
```

---

## Local development

```bash
cd serx-webhooks
python3.12 -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
pytest                                    # 7 tests; uses fake Supabase, no env needed
ruff check app/ tests/                    # lint
```

Do NOT run uvicorn locally with bare shell env vars (`SUPABASE_URL=... uvicorn ...`).
If you need to exercise the full stack locally, use `doppler run -- uvicorn app.main:app`
once you've authenticated with `doppler login` against the right project/config.

---

## Cutover plan (Phase 1 → Cal.com live traffic)

Not yet done. When ready:

1. In Doppler, set `CAL_WEBHOOK_SECRET` to a fresh value (32+ bytes).
2. Railway auto-redeploys.
3. In Cal.com dashboard → Webhooks, **add a new subscription** (don't modify
   the existing one yet):
   - URL: `https://serx-webhooks-ingest-production.up.railway.app/webhooks/cal`
   - Secret: same value you put in Doppler
   - Triggers: `BOOKING_CREATED`, `BOOKING_CANCELLED`, `BOOKING_RESCHEDULED`, `MEETING_STARTED`, `MEETING_ENDED` (all of them — this service is dumb by design).
4. Trigger a real test booking on Cal.com. Verify:
   - Railway logs show `webhook_stored ... signature_valid=True`
   - `select count(*) from webhook_events_raw where source='cal.com' and signature_valid=true;` > 0
5. Once confident, disable the old Cal.com webhook subscription pointing at
   `service-engine-x-api`. Leave the code in place (the directive explicitly
   forbade touching it).

### Rollback

If this service misbehaves, re-enable the old Cal.com webhook subscription
pointing at `service-engine-x-api/.../cal_webhooks`. The old handler still
exists, untouched.

---

## Phase 2+ roadmap (not in scope here)

Future phases, in rough priority order:

1. **Processor worker.** A second process (same or new service) that reads `status='received'` rows from `webhook_events_raw`, extracts the fields it cares about (organizer email, booking uid, event type), resolves `org_id` / `user_id`, and writes projected rows. Transitions `status` to `processed` / `failed`.
2. **Managed-agent dispatch.** Based on the route table (to be built), fan out processed events to managed agents.
3. **Non-Cal.com sources.** Generalize `/webhooks/<source>` — the `source` column already exists; just need more routers.
4. **Durability during Supabase outages.** Local disk spool if the insert fails. Not needed in phase 1 because Cal.com retries on non-2xx and we never return non-2xx.
5. **Observability.** Structured logs are in place; add metrics + trace IDs.
6. **CI boundary check.** Once phase 2 code exists in `service-engine-x-api`, add a CI check that `serx-webhooks/` does not import from any sibling folder.

---

## File / line reference

| File                                          | Purpose                                | Lines |
|-----------------------------------------------|----------------------------------------|-------|
| `Dockerfile`                                  | Image build + Doppler CLI + CMD        |   23  |
| `railway.toml`                                | Railway build/deploy config            |    9  |
| `pyproject.toml`                              | Deps + ruff config                     |   33  |
| `migrations/001_webhook_events_raw.sql`       | Table + indexes                        |   21  |
| `app/main.py`                                 | FastAPI app + CORS + router wiring     |   31  |
| `app/config.py`                               | pydantic-settings                      |   22  |
| `app/database.py`                             | Cached Supabase client factory         |   16  |
| `app/routers/health.py`                       | `/health/live`, `/health/ready`        |   29  |
| `app/routers/cal.py`                          | `/webhooks/cal` + HMAC + background    |  107  |
| `tests/test_webhook_smoke.py`                 | 7 smoke tests                          |  197  |

---

## Contact / context dump for next AI agent

- This service is **phase 1 of an intentionally minimal ingestion pipeline**. Resist the temptation to make it smarter. The whole point is to stop losing webhooks; parsing/routing belongs in a downstream processor.
- `service-engine-x-api/app/routers/cal_webhooks.py` is **off-limits** — do not refactor it, do not delete it, do not add comments. It still runs in parallel.
- The shared Supabase project contains three raw-event tables: `cal_webhook_events_raw` (old, v1), `cal_raw_events` (old, v2 unified), and `webhook_events_raw` (this service, v3). Do not cross-reference or merge.
- `webhooks-prod` is the only branch that carries `serx-webhooks/` code. Don't fast-forward it into `main` unless you have a reason.
- The directive file for the original scaffolding is gone from the transcript but was comprehensive; re-derive from this README + the code itself when in doubt.
