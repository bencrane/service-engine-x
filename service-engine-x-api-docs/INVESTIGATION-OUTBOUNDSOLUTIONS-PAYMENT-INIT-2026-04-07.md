# Investigation Report: `outboundsolutions.com/p/9d5bb180` Payment Init Failure

## Scope

Investigate why Stripe payment initialization still fails on the frontend after:
- backend short-ID payment-intent fix was deployed
- frontend route in `os-new-marketing-site-v1` was updated to dynamic `[proposalId]`

No fixes were applied in this investigation. This is a diagnosis-only handoff.

## Executive Summary

The current failure is **not** the old backend UUID mismatch anymore.

The live API now accepts short proposal IDs for payment-intent and returns `200`.
The likely active issue is a **CORS origin mismatch**:
- user lands on `https://www.outboundsolutions.com/p/9d5bb180` (apex redirects to `www`)
- API allows `https://outboundsolutions.com` origin
- API rejects `https://www.outboundsolutions.com` origin with `400 Disallowed CORS origin`

This exactly matches the UI symptom shown in screenshot:
`Network/init error: Load failed` (browser fetch blocked at network layer during CORS/preflight).

## Reproduction Evidence

### 1) Backend short-ID payment-intent is now healthy

`GET` works:

```bash
curl -i "https://api.serviceengine.xyz/api/public/proposals/9d5bb180"
```

Observed: `HTTP/2 200` with proposal payload (`id = 9d5bb180-c8e8-4968-9c1f-063d9d5f65c7`).

`POST` works with short ID:

```bash
curl -i -X POST "https://api.serviceengine.xyz/api/public/proposals/9d5bb180/payment-intent"
```

Observed: `HTTP/2 200` with JSON including `client_secret`, `payment_intent_id`, `amount`.

This rules out the prior `22P02 invalid input syntax for type uuid` root cause.

### 2) `www` origin is rejected by API CORS

Allowed origin (`apex`) preflight:

```bash
curl -i -X OPTIONS \
  "https://api.serviceengine.xyz/api/public/proposals/9d5bb180/payment-intent" \
  -H "Origin: https://outboundsolutions.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type"
```

Observed: `HTTP/2 200`, includes:
- `access-control-allow-origin: https://outboundsolutions.com`

Rejected origin (`www`) preflight:

```bash
curl -i -X OPTIONS \
  "https://api.serviceengine.xyz/api/public/proposals/9d5bb180/payment-intent" \
  -H "Origin: https://www.outboundsolutions.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type"
```

Observed: `HTTP/2 400` body:
- `Disallowed CORS origin`

### 3) Frontend route actually resolves to `www`

```bash
curl -I "https://outboundsolutions.com/p/9d5bb180"
```

Observed: `HTTP/2 307` redirect to:
- `https://www.outboundsolutions.com/p/9d5bb180`

So browser origin during client fetch is expected to be `https://www.outboundsolutions.com`.

## Frontend Code Path Review (`os-new-marketing-site-v1`)

File:
- `src/app/p/[proposalId]/page.tsx`

Relevant behavior:
- Reads route param via `useParams()`
- Calls:
  - `GET https://api.serviceengine.xyz/api/public/proposals/${proposalId}`
  - `POST https://api.serviceengine.xyz/api/public/proposals/${proposalId}/payment-intent`
- On thrown fetch error, shows:
  - `Network/init error: ${err.message}`

This error format aligns with browser-level CORS rejection (`TypeError: Failed to fetch` / `Load failed`).

## Why This Looks Like CORS, Not Stripe SDK

- Failure happens during initial API fetch path before Stripe confirm flow.
- API endpoint itself is healthy when called directly (server-to-server curl).
- Browser-only failure string is generic network/init (typical CORS symptom).
- Origin-specific preflight test reproduces reject on `www`.

## Likely Root Cause

Production API CORS configuration is missing `https://www.outboundsolutions.com` in allowed origins.

Backend code uses:
- `allow_origins=settings.CORS_ORIGINS` in `app/main.py`

Given observed behavior, deployed `CORS_ORIGINS` appears to include apex domain but not `www`.

## What the Next Agent Should Do (Fix Scope)

1. Update production CORS origin allowlist to include both:
   - `https://outboundsolutions.com`
   - `https://www.outboundsolutions.com`
2. Redeploy API.
3. Validate from browser context on `https://www.outboundsolutions.com/p/9d5bb180` that payment init succeeds.
4. Keep short-ID support verification in place (already working).

## Ruled-Out Causes

- Route param bug in `os-new-marketing-site-v1`: dynamic route is present and used.
- Old backend UUID parsing mismatch on payment-intent: resolved in current production behavior.
- Missing publishable key (for this proposal): GET returns `stripe_publishable_key`.

