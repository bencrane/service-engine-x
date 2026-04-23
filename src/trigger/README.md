# Trigger.dev — SERX ticker

This directory contains the Trigger.dev task definitions for the SERX
time-based event scheduler. Trigger.dev runs as a **dumb clock**: it fires
on a cron schedule and POSTs to a single internal endpoint on the SERX API.
All scheduling logic (which meetings are due, idempotency, dispatch to
managed-agents) lives server-side, not here.

## Architecture

```
    Trigger.dev (cron)                       SERX API                      managed-agents-x-api
    ───────────────────                      ──────────                      ────────────────────
    serx:scheduler-tick                      /api/internal/scheduler/        /sessions/from-event
    every 6h                 ───POST──▶      dispatch-due-preframes   ───▶   (per due meeting)
                                             • query due meetings
                                             • insert webhook_events_raw row
                                             • dispatch to OPEX
                                             • record outcome
```

Adding a new time-based event (e.g. `meeting_reminder_due`, `no_show_nudge_due`)
does **not** require a new Trigger.dev task. It only requires appending a new
`EventConfig` in the server-side dispatcher. The ticker URL stays the same.

## Key files

| File | Role |
|---|---|
| [`trigger.config.ts`](../../trigger.config.ts) | Trigger.dev project config (project id `proj_iuvlrmaxdwoykmvolbie`, runtime, retries, task dir) |
| [`scheduler-tick.ts`](./scheduler-tick.ts) | The only production task. Cron `0 */6 * * *`. POSTs to the dispatch endpoint. |
| [`example.ts`](./example.ts) | Starter stub from `npx trigger.dev init`. Safe to delete once more real tasks exist. |
| [`../../service-engine-x-api/app/routers/internal_scheduler.py`](../../service-engine-x-api/app/routers/internal_scheduler.py) | Server-side dispatcher. Owns all scheduling logic. |
| [`../../service-engine-x-api/migrations/019_scheduler_preframe.sql`](../../service-engine-x-api/migrations/019_scheduler_preframe.sql) | Backing schema: `meetings.preframe_sent_at` + idempotency indexes on `webhook_events_raw`. |

## Environment variables

The task reads two env vars from `process.env`:

- `SERX_API_URL` — base URL of the SERX API (e.g. `https://api.serx.run`). No trailing slash required.
- `SERX_INTERNAL_TOKEN` — must match the SERX API's `INTERNAL_API_KEY` (sent as `Authorization: Bearer <token>`).

**Both must be set inside Trigger.dev**, per environment (dev / staging / prod).
There is no Doppler integration wired in — `process.env` in a Trigger.dev task
only contains what's configured in the Trigger.dev project's env settings.

Options if you want Doppler-sourced secrets:
1. Configure a Doppler → Trigger.dev sync integration (recommended — values still land in `process.env`).
2. Runtime Doppler fetch in the task using a Doppler service token (adds an API call per run; not recommended).

## Cron cadence

Currently `0 */6 * * *` (every 6 hours). The original directive asked for 15-minute
granularity; an operator note requested 6h while the pipeline stabilises. When tightening
the cadence, re-evaluate the SERX API dispatch-loop timeout (`SCHEDULER_DISPATCH_TIMEOUT_SECONDS`)
and the idempotency index — overlapping ticks are fine (the DB uniqueness guard blocks
duplicates), but a too-short cadence wastes dispatch work.

Edit `CRON_EVERY_6_HOURS` in [`scheduler-tick.ts`](./scheduler-tick.ts); don't inline the
cron string elsewhere.

## Deploying

Trigger.dev deploys are out-of-band from the Next.js / FastAPI services:

```bash
npx trigger.dev@latest deploy
```

Env vars are managed via the Trigger.dev dashboard or `npx trigger.dev env`.
Do **not** expect `.env` / Doppler values from the host to flow through.
