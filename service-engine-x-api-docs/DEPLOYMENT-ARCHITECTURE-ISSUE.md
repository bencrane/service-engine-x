# Service-Engine-X Deployment Architecture Issue

**Date:** 2026-02-08
**Status:** BLOCKED - Architecture mismatch between development and deployment

---

## Executive Summary

We built a DocRaptor/Documenso e-signature integration for proposals in the **FastAPI backend**, but discovered that the production API at `api.serviceengine.xyz` is actually a **Next.js app on Vercel** with its own API routes - NOT the FastAPI. The FastAPI is deployed on Railway but is **unexposed** (no public URL).

---

## Project Structure

```
/Users/benjamincrane/service-engine-x/
├── app/                          # Next.js App Router (DEPLOYED ON VERCEL)
│   └── api/                      # Next.js API routes (THIS IS WHAT api.serviceengine.xyz USES)
│       ├── proposals/
│       │   ├── route.ts          # list-proposals, create-proposal
│       │   └── [id]/
│       │       ├── route.ts      # retrieve-proposal
│       │       ├── send/route.ts # send-proposal
│       │       └── sign/route.ts # sign-proposal
│       ├── clients/
│       ├── services/
│       └── ...
├── next.config.ts
├── package.json
│
├── service-engine-x-api/         # FastAPI backend (DEPLOYED ON RAILWAY - UNEXPOSED)
│   ├── app/
│   │   ├── main.py
│   │   └── routers/
│   │       └── proposals.py      # <-- NEW CODE IS HERE (DocRaptor/Documenso)
│   └── requirements.txt
│
├── service-engine-x-api-docs/    # Documentation
└── migrations/                   # Database migrations
```

---

## The Two APIs

### 1. Next.js API Routes (Vercel) - PRODUCTION
- **URL:** `api.serviceengine.xyz`
- **Location:** `/service-engine-x/app/api/`
- **How it works:** Each route.ts file handles requests directly, calling Supabase
- **Deployment:** Automatic via Vercel on git push
- **Status:** Working, but MISSING the new public/webhook endpoints

### 2. FastAPI (Railway) - NOT EXPOSED
- **URL:** None (service is "Unexposed")
- **Location:** `/service-engine-x/service-engine-x-api/`
- **How it works:** Full FastAPI app with routers
- **Deployment:** Automatic via Railway on git push
- **Status:** Code deployed, but no public URL assigned

---

## What We Built Today

### Goal
Enable proposals to be viewed and signed at a public URL like `revenueactivation.com/p/{proposal_id}` using:
1. **DocRaptor** - Convert proposal HTML to PDF
2. **Documenso** - E-signature with embeddable signing widget

### Code Added (to FastAPI - `/service-engine-x-api/`)

1. **Migration:** `migrations/004_add_documenso_to_proposals.sql`
   - Added `documenso_document_id` and `documenso_signing_token` columns to `proposals` table
   - **Migration was run successfully**

2. **Updated `POST /api/proposals/{id}/send`** in `app/routers/proposals.py`
   - Generates HTML from proposal
   - Converts to PDF via DocRaptor
   - Uploads to Documenso
   - Stores signing token on proposal

3. **New endpoint `GET /api/public/proposals/{id}`**
   - No authentication required
   - Returns proposal data + signing token for frontend to embed Documenso

4. **New endpoint `POST /api/webhooks/documenso`**
   - Receives signing completion events from Documenso
   - Triggers engagement/project/order creation

5. **Dependencies added:** `docraptor`, `requests` in `requirements.txt`

### Commits
- `eed6529` - Refactor proposals API to project-centric model
- `824d6d8` - Add DocRaptor/Documenso integration for proposal signing

---

## The Problem

The new endpoints exist in **FastAPI** (`/service-engine-x-api/`), but:

1. `api.serviceengine.xyz` points to **Next.js on Vercel**, not FastAPI
2. The Railway FastAPI deployment is **"Unexposed"** - no public URL
3. The Next.js API routes (`/app/api/`) do NOT have the new public/webhook endpoints

When we try to access:
```
https://api.serviceengine.xyz/api/public/proposals/{id}
```

We get a **404** because:
- Next.js doesn't have `/api/public/proposals/[id]/route.ts`
- The request never reaches FastAPI

---

## Test Data Created

A test proposal was created in the database:

```
Proposal ID: d0e3619d-daa1-4ece-b234-9ba6ba3332ef
Client: Sarah Johnson (sarah.johnson@acmecorp.io)
Company: Acme Corporation
Status: 1 (Sent) - manually set for testing
Total: $12,500.00
Items:
  - Sales Pipeline Optimization ($7,500)
  - Outbound Campaign Setup ($5,000)
Documenso Token: test-signing-token-abc (fake, for testing)
```

API Token for testing:
```
sengx_nXfodU6C0JO_SyUQAJIfCeECrcyCSc65lQWgX-sFDUJBWczl
```

---

## Solutions (Pick One)

### Option A: Expose FastAPI on Railway
1. Go to Railway dashboard → service-engine-x → Settings → Networking
2. Click "Generate Domain" to get a public URL
3. Use that URL directly: `https://xxx.up.railway.app/api/public/proposals/{id}`
4. Update frontend to call Railway URL for these specific endpoints

**Pros:** Quick, no code changes
**Cons:** Two different API URLs (Vercel for most, Railway for public/webhooks)

### Option B: Add Routes to Next.js API
1. Create `/app/api/public/proposals/[id]/route.ts`
2. Create `/app/api/webhooks/documenso/route.ts`
3. Implement the same logic as FastAPI (or proxy to Railway)

**Pros:** Single API URL (`api.serviceengine.xyz`)
**Cons:** Duplicating logic or adding proxy complexity

### Option C: Migrate Everything to FastAPI
1. Expose FastAPI on Railway with custom domain
2. Point `api.serviceengine.xyz` to Railway instead of Vercel
3. Deprecate Next.js API routes

**Pros:** Single source of truth, Python backend
**Cons:** Larger migration effort

### Option D: Proxy from Next.js to FastAPI
1. Expose FastAPI on Railway (internal or public)
2. Create catch-all route in Next.js that proxies to FastAPI
3. Keep Next.js as the public-facing API

**Pros:** Gradual migration path
**Cons:** Added latency, complexity

---

## Environment Variables Needed

For whichever solution, these are required:

```
DOCRAPTOR_API_KEY=oUcqyfynOYOBkEIV8_IU
DOCUMENSO_API_KEY=api_r4fv8167lra8c3dh
DOCUMENSO_URL=https://app.documenso.com
```

Currently hardcoded in FastAPI as defaults, should be moved to env vars in production.

---

## Files Modified in This Session

### FastAPI (`/service-engine-x-api/`)
- `app/main.py` - Added public_proposals_router, webhooks_router
- `app/routers/__init__.py` - Exported new routers
- `app/routers/proposals.py` - Added DocRaptor/Documenso integration, public endpoint, webhook
- `app/models/proposals.py` - Updated ProposalItemInput (name, description, price, optional service_id)
- `requirements.txt` - Added docraptor, requests

### Migrations (`/migrations/`)
- `003_proposal_items_project_centric.sql` - Added name/description to proposal_items, made service_id nullable
- `004_add_documenso_to_proposals.sql` - Added documenso columns to proposals

### Documentation (`/service-engine-x-api-docs/`)
- `PROPOSAL-API-CHANGES.md` - Documents the project-centric proposal model

---

## Database State

Both migrations have been applied to:
```
postgresql://postgres:***@db.htgfjmjuzcqffdzuiphg.supabase.co:5432/postgres
```

The `proposals` table has:
- `documenso_document_id` column (nullable)
- `documenso_signing_token` column (nullable)

The `proposal_items` table has:
- `name` column (NOT NULL)
- `description` column (nullable)
- `service_id` column (now nullable)

---

## Next Steps

1. **Decide on architecture** (Options A-D above)
2. **Expose FastAPI on Railway** (needed for any option except B)
3. **Test the full flow:**
   - Create proposal
   - Send proposal (generates PDF, uploads to Documenso)
   - View public proposal page
   - Sign via Documenso
   - Verify engagement/projects/order created
4. **Build frontend `/p/{id}` route** that fetches from public API and embeds Documenso

---

## Reference: Documenso Integration Pattern

From the working implementation in `/Users/benjamincrane/data-enrichment-orchestration-v1/`:

```
Form Submit → HTML Generated → DocRaptor (PDF) → Documenso (e-sign) → Store Token → Frontend Embed
```

See `/data-enrichment-orchestration-v1/documentation/global/proposal_generation_architecture.md` for full details.
