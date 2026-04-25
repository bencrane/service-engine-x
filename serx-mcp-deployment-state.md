# SERX MCP Deployment State (Railway + Doppler + Docker)

Last updated: 2026-04-10 (post-migration to dedicated Railway app)
Scope: `service-engine-x-mcp` deployment flow and current known-good state.

## Executive status

`serx-mcp` is deployed via Railway using a Dockerfile-based build.  
Main failure classes encountered during rollout were:

1. Docker build-time failure (`tsc: not found`)
2. Runtime secret injection/context mismatch (app boot failed with required `SERX_*` env vars missing)

Both were diagnosed and addressed with infrastructure/config changes.

Current status:

- `serx-mcp` was moved out of the previous/shared Railway app into its own dedicated Railway app.
- After the app split, service reported as live again.
- This strongly supports prior diagnosis that cross-service/app configuration context was contaminating runtime env resolution.

## Service and endpoints

- Railway service name: `serx-mcp`
- Public host: `serx-mcp-production.up.railway.app`
- Dockerfile path: `service-engine-x-mcp/Dockerfile`
- Runtime entrypoint: `doppler run -- npm run start` (from Dockerfile `CMD`)
- Health endpoint: `/healthz`

## Railway app migration note (critical)

The service was originally running inside a Railway app that also hosted other services.
During troubleshooting, `serx-mcp` repeatedly crashed with missing required `SERX_*` env vars even though secrets existed in Doppler.

After moving `serx-mcp` into a dedicated Railway app, deployment became live.

Interpretation:

- Service isolation at the Railway app boundary removed a configuration/context collision.
- Prior environment ambiguity (including signals around `hq-dev` context resolution) is treated as an app-level config bleed risk.
- Dedicated app deployment is now the recommended baseline for `serx-mcp`.

## Repository and key files

- Service code: `service-engine-x-mcp/`
- Dockerfile: `service-engine-x-mcp/Dockerfile`
- Docker ignore: `service-engine-x-mcp/.dockerignore`
- Env validation: `service-engine-x-mcp/src/env.ts`
- HTTP server boot and health route: `service-engine-x-mcp/src/server.ts`

## Final container strategy

The service was moved to a multi-stage Docker build:

1. `build` stage:
   - installs dev dependencies
   - compiles TypeScript (`npm run build`)
2. `prod-deps` stage:
   - installs production dependencies only (`npm ci --omit=dev`)
3. `runtime` stage:
   - includes Doppler CLI
   - copies `dist`, production `node_modules`, and `package.json`
   - runs as non-root (`USER node`)
   - sets `NODE_ENV=production`
   - exposes healthcheck against `/healthz`

## Why this was necessary

### Build failure root cause

Initial deployment failed with:

- `sh: 1: tsc: not found`
- Docker step failed on `RUN npm run build`

Cause:

- `NODE_ENV=production` affected dependency install behavior before build, so `typescript` (dev dependency) was unavailable during compile.

Fix path:

- first tactical fix: install dev deps for build then prune
- final fix: multi-stage Dockerfile to separate build-time vs runtime deps cleanly

### Runtime failure root cause

After build issues were fixed, startup failed repeatedly with:

- `Invalid MCP environment configuration: SERX_MCP_AUTH_TOKEN: Required; SERX_INTERNAL_API_BASE_URL: Required; SERX_INTERNAL_API_KEY: Required; SERX_SERVICE_API_TOKEN: Required`

This comes directly from `src/env.ts` schema validation.

Important diagnosis:

- Secrets existed in Doppler for `serx-mcp/prd`
- Runtime process still did not receive required vars
- Therefore failure was not secret creation, but context/injection mismatch

Contributing signal:

- Using the provided Doppler token without explicit project/config attempted an inaccessible project (`hq-dev`) in local shell context
- Explicitly targeting `--project serx-mcp --config prd` returned the expected `SERX_*` keys

This pointed to wrong Doppler context resolution in runtime path, not missing secrets.

## Railway configuration expected (current target state)

Service-level env vars for `serx-mcp` should be:

- `DOPPLER_TOKEN=<service token scoped to serx-mcp/prd>`
- `DOPPLER_PROJECT=serx-mcp`
- `DOPPLER_CONFIG=prd`

Operational notes:

- Keep `serx-mcp` in its own Railway app (do not re-co-locate with unrelated services).
- Use Dockerfile as single source of truth for build/start behavior.
- Remove/leave empty Railway "Custom Build Command" for this service when Dockerfile is used.
- Do not duplicate build logic (`npm ci && npm run build`) in Railway custom command and Dockerfile at the same time.

## Commits relevant to this rollout

- `9ee3411` - Fix MCP Docker build to include TypeScript at compile time
- `57569f4` - Refactor MCP container to multi-stage production runtime

## Validation performed

### Build validation

- `npm ci --include=dev && npm run build` passed in `service-engine-x-mcp`
- Docker image builds succeeded after changes

### Runtime artifact validation

- Verified final runtime image excludes TypeScript:
  - check returned `TYPESCRIPT_ABSENT`

### Image metrics

- Prior single-stage fixed image: `459MB`
- Multi-stage runtime image: `397MB`
- Reduction: ~`62MB`

## Known pitfalls for next agent

1. If logs show `Invalid MCP environment configuration ... Required`, do not debug API code first.  
   This is environment injection failure until proven otherwise.

2. If Doppler secrets exist but app still fails, check context resolution:
   - project/config selection
   - whether service is in a shared app with inherited/conflicting configuration
   - service-scoped env vars on Railway
   - start command actually running through `doppler run`

3. Keep Docker and Railway responsibilities separate:
   - Dockerfile handles build/runtime setup
   - Railway supplies env and deployment orchestration

## Quick triage checklist (if issue recurs)

1. Confirm service logs include `> node dist/index.js` and any env validation errors.
2. Confirm required vars in `src/env.ts` still match Doppler keys exactly.
3. Confirm Railway service env has:
   - `DOPPLER_TOKEN`
   - `DOPPLER_PROJECT=serx-mcp`
   - `DOPPLER_CONFIG=prd`
4. Confirm Dockerfile `CMD` remains:
   - `["doppler", "run", "--", "npm", "run", "start"]`
5. Redeploy service after env changes.
6. Verify `GET /healthz` returns 200.
7. If recurrent env mismatch persists, move/keep `serx-mcp` in a dedicated Railway app before further code changes.

## Current conclusion

Deployment architecture is now sane:

- deterministic Docker build
- reduced runtime image
- strict env schema at boot
- Doppler-based secret injection at process start

The remaining operational risk is configuration drift in Railway env/context, not code path correctness.
