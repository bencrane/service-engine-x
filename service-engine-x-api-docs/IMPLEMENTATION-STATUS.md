# API Implementation Status

This document tracks which API endpoints are implemented in the **FastAPI backend**.

**Last Updated:** 2026-02-08
**Backend:** FastAPI (Python) on Railway
**Production URL:** `https://api.serviceengine.xyz`

---

## Summary

| Category | Implemented | Total | Status |
|----------|-------------|-------|--------|
| Health | 1 | 1 | ✅ |
| Clients | 5 | 5 | ✅ |
| Services | 5 | 5 | ✅ |
| Orders | 5 | 5 | ✅ |
| Order Tasks | 6 | 6 | ✅ |
| Order Messages | 3 | 3 | ✅ |
| Proposals | 5 | 5 | ✅ |
| Invoices | 7 | 7 | ✅ |
| Tickets | 5 | 5 | ✅ |
| Engagements | 5 | 5 | ✅ |
| Projects | 5 | 5 | ✅ |
| Conversations | 4 | 4 | ✅ |
| **TOTAL** | **56** | **56** | ✅ |

---

## Health

| Endpoint | Method | Implementation | Status |
|----------|--------|----------------|--------|
| `/api/health` | GET | `routers/health.py` | ✅ |

---

## Clients

| Endpoint | Method | Implementation | Status |
|----------|--------|----------------|--------|
| `/api/clients` | GET | `routers/clients.py` | ✅ |
| `/api/clients` | POST | `routers/clients.py` | ✅ |
| `/api/clients/{id}` | GET | `routers/clients.py` | ✅ |
| `/api/clients/{id}` | PUT | `routers/clients.py` | ✅ |
| `/api/clients/{id}` | DELETE | `routers/clients.py` | ✅ |

---

## Services

| Endpoint | Method | Implementation | Status |
|----------|--------|----------------|--------|
| `/api/services` | GET | `routers/services.py` | ✅ |
| `/api/services` | POST | `routers/services.py` | ✅ |
| `/api/services/{id}` | GET | `routers/services.py` | ✅ |
| `/api/services/{id}` | PUT | `routers/services.py` | ✅ |
| `/api/services/{id}` | DELETE | `routers/services.py` | ✅ |

---

## Orders

| Endpoint | Method | Implementation | Status |
|----------|--------|----------------|--------|
| `/api/orders` | GET | `routers/orders.py` | ✅ |
| `/api/orders` | POST | `routers/orders.py` | ✅ |
| `/api/orders/{id}` | GET | `routers/orders.py` | ✅ |
| `/api/orders/{id}` | PUT | `routers/orders.py` | ✅ |
| `/api/orders/{id}` | DELETE | `routers/orders.py` | ✅ |

---

## Order Tasks

| Endpoint | Method | Implementation | Status |
|----------|--------|----------------|--------|
| `/api/orders/{id}/tasks` | GET | `routers/orders.py` | ✅ |
| `/api/orders/{id}/tasks` | POST | `routers/orders.py` | ✅ |
| `/api/order-tasks/{id}` | PUT | `routers/order_tasks.py` | ✅ |
| `/api/order-tasks/{id}` | DELETE | `routers/order_tasks.py` | ✅ |
| `/api/order-tasks/{id}/complete` | POST | `routers/order_tasks.py` | ✅ |
| `/api/order-tasks/{id}/complete` | DELETE | `routers/order_tasks.py` | ✅ |

---

## Order Messages

| Endpoint | Method | Implementation | Status |
|----------|--------|----------------|--------|
| `/api/orders/{id}/messages` | GET | `routers/orders.py` | ✅ |
| `/api/orders/{id}/messages` | POST | `routers/orders.py` | ✅ |
| `/api/order-messages/{id}` | DELETE | `routers/order_messages.py` | ✅ |

---

## Proposals

| Endpoint | Method | Implementation | Status |
|----------|--------|----------------|--------|
| `/api/proposals` | GET | `routers/proposals.py` | ✅ |
| `/api/proposals` | POST | `routers/proposals.py` | ✅ |
| `/api/proposals/{id}` | GET | `routers/proposals.py` | ✅ |
| `/api/proposals/{id}/send` | POST | `routers/proposals.py` | ✅ |
| `/api/proposals/{id}/sign` | POST | `routers/proposals.py` | ✅ |
| `/api/public/proposals/{id}` | GET | `routers/proposals.py` | ✅ (No Auth) |

---

## Invoices

| Endpoint | Method | Implementation | Status |
|----------|--------|----------------|--------|
| `/api/invoices` | GET | `routers/invoices.py` | ✅ |
| `/api/invoices` | POST | `routers/invoices.py` | ✅ |
| `/api/invoices/{id}` | GET | `routers/invoices.py` | ✅ |
| `/api/invoices/{id}` | PUT | `routers/invoices.py` | ✅ |
| `/api/invoices/{id}` | DELETE | `routers/invoices.py` | ✅ |
| `/api/invoices/{id}/charge` | POST | `routers/invoices.py` | ✅ |
| `/api/invoices/{id}/mark_paid` | POST | `routers/invoices.py` | ✅ |

---

## Tickets

| Endpoint | Method | Implementation | Status |
|----------|--------|----------------|--------|
| `/api/tickets` | GET | `routers/tickets.py` | ✅ |
| `/api/tickets` | POST | `routers/tickets.py` | ✅ |
| `/api/tickets/{id}` | GET | `routers/tickets.py` | ✅ |
| `/api/tickets/{id}` | PUT | `routers/tickets.py` | ✅ |
| `/api/tickets/{id}` | DELETE | `routers/tickets.py` | ✅ |

---

## Engagements

| Endpoint | Method | Implementation | Status |
|----------|--------|----------------|--------|
| `/api/engagements` | GET | `routers/engagements.py` | ✅ |
| `/api/engagements` | POST | `routers/engagements.py` | ✅ |
| `/api/engagements/{id}` | GET | `routers/engagements.py` | ✅ |
| `/api/engagements/{id}` | PUT | `routers/engagements.py` | ✅ |
| `/api/engagements/{id}` | DELETE | `routers/engagements.py` | ✅ |

---

## Projects

| Endpoint | Method | Implementation | Status |
|----------|--------|----------------|--------|
| `/api/projects` | GET | `routers/projects.py` | ✅ |
| `/api/projects` | POST | `routers/projects.py` | ✅ |
| `/api/projects/{id}` | GET | `routers/projects.py` | ✅ |
| `/api/projects/{id}` | PUT | `routers/projects.py` | ✅ |
| `/api/projects/{id}` | DELETE | `routers/projects.py` | ✅ |

---

## Conversations

| Endpoint | Method | Implementation | Status |
|----------|--------|----------------|--------|
| `/api/conversations` | GET | `routers/conversations.py` | ✅ |
| `/api/conversations` | POST | `routers/conversations.py` | ✅ |
| `/api/conversations/{id}` | GET | `routers/conversations.py` | ✅ |
| `/api/conversations/{id}/messages` | POST | `routers/conversations.py` | ✅ |

---

## Webhooks

| Endpoint | Method | Implementation | Status |
|----------|--------|----------------|--------|
| `/api/webhooks/documenso` | POST | `routers/proposals.py` | ✅ (No Auth) |

---

## Architecture Notes

### Deployment (as of 2026-02-08)
- **Backend:** FastAPI on Railway
- **URL:** `https://api.serviceengine.xyz`
- **Database:** Supabase (PostgreSQL)
- **Auth:** Bearer token (SHA-256 hashed, stored in `api_tokens` table)

### Previous Architecture (Deprecated)
- Next.js API routes on Vercel have been deprecated
- All API traffic now goes directly to FastAPI on Railway

### Multi-Tenancy
- All endpoints filter by `org_id` from the authenticated token
- Data isolation is enforced at the query level

---

## File Reference

All implementations are in `/service-engine-x-api/app/`:

```
app/
├── main.py              # FastAPI app, CORS, error handlers
├── config.py            # Environment settings
├── database.py          # Supabase client
├── auth/
│   ├── dependencies.py  # get_current_org auth dependency
│   └── utils.py         # Token hashing utilities
├── models/              # Pydantic request/response schemas
│   ├── clients.py
│   ├── services.py
│   ├── orders.py
│   ├── proposals.py
│   ├── invoices.py
│   ├── tickets.py
│   ├── engagements.py
│   ├── projects.py
│   └── conversations.py
└── routers/             # API endpoint handlers
    ├── clients.py
    ├── services.py
    ├── orders.py
    ├── order_tasks.py
    ├── order_messages.py
    ├── proposals.py
    ├── invoices.py
    ├── tickets.py
    ├── engagements.py
    ├── projects.py
    └── conversations.py
```
