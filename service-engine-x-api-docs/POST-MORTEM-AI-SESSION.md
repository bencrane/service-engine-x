# Post-Mortem: DocRaptor/Documenso Integration Session

**Date:** 2026-02-08
**Session Duration:** Extended multi-hour session
**Outcome:** Code complete but not deployable; architecture mismatch discovered late

---

## What Went Wrong

### 1. AI Did Not Ask About Deployment Architecture Upfront

The AI proceeded to build the entire DocRaptor/Documenso integration in FastAPI without first verifying:

- Where is the FastAPI actually deployed?
- Is it publicly accessible?
- What URL will the frontend use to call these endpoints?

**The user had a clear intent to use FastAPI directly.** The AI should have confirmed the deployment situation before writing any code, not after.

### 2. AI Made Assumptions Instead of Asking

When discovering the architecture mismatch late in the session, the AI immediately jumped to proposing solutions (proxy to Next.js, add routes to Next.js, etc.) instead of:

1. Stopping to acknowledge the mistake
2. Asking the user what their intended deployment architecture was
3. Asking why FastAPI was chosen and what the plan was for exposing it

The user chose FastAPI for a reason. The AI should have asked what that reason was.

### 3. AI Built in the Wrong Place Without Verification

The AI knew:
- The project has both Next.js (`/app/api/`) and FastAPI (`/service-engine-x-api/`)
- The user asked to build in FastAPI
- There was an existing reference implementation in another project using FastAPI

The AI did NOT verify:
- That FastAPI was accessible at a public URL
- How the frontend would reach the FastAPI endpoints
- Whether Railway was configured to expose the service

This should have been the **first** question, not the last discovery.

### 4. Late-Session Frustration Was Avoidable

By the time the architecture mismatch was discovered:
- Multiple hours had been invested
- Code was written, tested locally, committed, deployed
- Database migrations were run
- Test data was created

The user was understandably frustrated. All of this work is valid and correct - but it's not reachable. This entire situation could have been avoided with one question at the start:

> "Before I build this in FastAPI, can you confirm the FastAPI is publicly accessible? What URL will the frontend use to call these endpoints?"

---

## What the AI Should Have Done

### At Session Start (Proposal Refactoring)

1. Confirm the deployment architecture
2. Ask: "I see both Next.js API routes and FastAPI. Which one serves production traffic at api.serviceengine.xyz?"
3. If unsure, ask the user to clarify before proceeding

### Before Adding DocRaptor/Documenso

1. Ask: "This integration requires public endpoints for proposal viewing and webhooks. Where should these be deployed?"
2. Ask: "Is the FastAPI on Railway exposed with a public URL?"
3. If the user wants FastAPI, confirm: "Should I proceed with FastAPI, and you'll handle exposing it on Railway?"

### When Discovering the Mismatch

1. Stop proposing solutions immediately
2. Acknowledge: "I should have asked about this before building"
3. Ask: "What was your intended deployment plan for FastAPI?"
4. Let the user drive the solution choice

---

## What Was Built (Still Valid)

All the code is correct and functional. It just needs the FastAPI to be exposed:

### FastAPI Code (`/service-engine-x-api/`)
- `POST /api/proposals/{id}/send` - Generates PDF via DocRaptor, uploads to Documenso
- `GET /api/public/proposals/{id}` - Public endpoint for viewing proposals (no auth)
- `POST /api/webhooks/documenso` - Receives signing completion events

### Database Migrations (Already Applied)
- `003_proposal_items_project_centric.sql` - Project-centric proposal items
- `004_add_documenso_to_proposals.sql` - Documenso columns on proposals

### Test Data (In Database)
- Proposal ID: `d0e3619d-daa1-4ece-b234-9ba6ba3332ef`
- API Token: `sengx_nXfodU6C0JO_SyUQAJIfCeECrcyCSc65lQWgX-sFDUJBWczl`

---

## The Fix

The user's intent was **direct FastAPI**. The fix is simple:

1. Go to Railway dashboard
2. Navigate to the service-engine-x service
3. Settings → Networking → Generate Domain
4. Use that Railway URL for the public/webhook endpoints

No code changes needed. No proxies. No Next.js routes. Just expose what was built.

---

## Lessons for Future AI Sessions

1. **Ask about deployment before building** - "Where will this run? Is it publicly accessible?"

2. **Don't assume infrastructure** - Just because code exists doesn't mean it's deployed or reachable

3. **When user chooses a technology, ask why** - Understanding intent prevents wrong assumptions

4. **When discovering mistakes, stop and ask** - Don't immediately propose solutions; let the user guide

5. **Verify assumptions explicitly** - "I'm assuming X, is that correct?" is always better than proceeding silently

---

## Summary

The AI built the right code in the right place (FastAPI, as requested), but failed to verify the deployment architecture upfront. This led to a frustrating late-session discovery that the FastAPI isn't publicly accessible.

The code is complete and correct. The user just needs to expose FastAPI on Railway to use it.

**The core failure was not asking questions when it mattered - at the start, not the end.**
