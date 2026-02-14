# Changelog

All notable changes to the Service Engine X API.

---

## 2026-02-13

### Added
- **Internal admin endpoint** for creating proposals (`POST /internal/proposals`)
  - Accepts `org_id` to create proposals for any org
  - Auto-sends email to client with signing link
  - Optional `email_subject` and `email_body` fields for custom emails
  - Uses `X-Internal-Key` header for auth

- **API keys for all orgs** - frontend can now authenticate per-org:
  - Revenue Activation
  - Outbound Solutions
  - Modern Full
  - Everything Automation
  - RevenueEngineer.com (new org added)

- **Cal.com email routing** - emails now send from correct domain based on organizer
  - Updated `calcom_ingest.py` with `FROM_EMAIL_MAP`

### Fixed
- **500 error on proposal creation** - added `.select("*")` to insert calls
  - Without this, Supabase doesn't return `created_at`, `updated_at` etc.
  - Serializer was failing on missing fields

- **Signed PDF generation** - built server-side HTML template
  - DocRaptor was failing on frontend HTML (external CSS references)
  - Now generates PDF entirely server-side

### Changed
- **Field naming** - renamed `client_*` fields to Account/Contact terminology:
  - `client_company` -> `account_name` (in API responses)
  - `client_email` -> `contact_email`
  - `client_name_f/l` -> `contact_name_f/l`
  - Database columns unchanged (mapped in serializers)

- **Default proposal email** - more direct tone, less "beta"

---

## Project Structure

```
service-engine-x-api/
├── app/
│   ├── auth/           # Authentication (API tokens, JWT sessions)
│   ├── models/         # Pydantic request/response schemas
│   ├── routers/        # API endpoints
│   │   ├── proposals.py    # Proposal CRUD, sign, send
│   │   ├── internal.py     # Admin endpoints (no org auth)
│   │   ├── engagements.py  # Client engagements
│   │   ├── orders.py       # Orders/payments
│   │   └── ...
│   ├── services/       # External services (Resend, Stripe, etc.)
│   ├── utils/          # Helpers (storage, formatting)
│   ├── config.py       # Environment settings
│   ├── database.py     # Supabase client
│   └── main.py         # FastAPI app, middleware, routes
├── migrations/         # SQL migrations
├── docs/               # Documentation
└── CHANGELOG.md        # This file
```

---

## API Authentication

### Per-Org API Keys (standard endpoints)
```
Authorization: Bearer <org_api_key>
POST /api/proposals
```

### Internal Admin Key (admin endpoints)
```
X-Internal-Key: <internal_key>
POST /internal/proposals
```

---

## Key Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/proposals` | POST | Bearer | Create proposal (draft) |
| `/api/proposals/{id}` | GET | Bearer | Get proposal |
| `/api/proposals/{id}/send` | POST | Bearer | Send proposal (draft -> sent) |
| `/api/proposals/{id}/sign` | POST | Public | Sign proposal |
| `/internal/proposals` | POST | X-Internal-Key | Create + send proposal for any org |
| `/api/public/proposals/{id}` | GET | Public | Get proposal for signing page |
