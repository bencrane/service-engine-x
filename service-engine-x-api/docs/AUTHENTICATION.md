# Authentication Guide

This document describes the authentication system used in Service Engine X API.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Authentication Methods](#2-authentication-methods)
3. [JWT Session Tokens](#3-jwt-session-tokens)
4. [API Tokens](#4-api-tokens)
5. [Auth Dependencies](#5-auth-dependencies)
6. [Configuration](#6-configuration)
7. [Database Schema](#7-database-schema)
8. [Usage Examples](#8-usage-examples)

---

## 1. Overview

The API supports two authentication methods:

| Method | Use Case | Storage | Expiration |
|--------|----------|---------|------------|
| **JWT Session** | User login (portal, dashboard) | Client-side | 72 hours (configurable) |
| **API Token** | Machine-to-machine integrations | Database | Optional (can be permanent) |

Both methods return an `AuthContext` containing:
- `org_id` - The tenant identifier (for multi-tenant isolation)
- `user_id` - The authenticated user
- `auth_method` - Either `"session"` or `"api_token"`

---

## 2. Authentication Methods

### Request Format

All authenticated requests must include the `Authorization` header:

```
Authorization: Bearer <token>
```

The token can be either a JWT session token or an API token. The system automatically detects which type it is.

### Authentication Flow

```
┌─────────────────┐
│  Authorization  │
│  Bearer <token> │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Try JWT first  │────▶│  Valid JWT?     │
│  (no DB call)   │     │  Return auth    │
└─────────────────┘     └─────────────────┘
         │ No
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Try API token  │────▶│  Valid token?   │
│  (DB lookup)    │     │  Return auth    │
└─────────────────┘     └─────────────────┘
         │ No
         ▼
┌─────────────────┐
│  401 Unauthorized│
└─────────────────┘
```

---

## 3. JWT Session Tokens

### Login Endpoint

```
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secret123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in_hours": 72,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name_f": "John",
    "name_l": "Doe",
    "name": "John Doe",
    "company": "Acme Inc",
    "phone": "+1234567890",
    "org_id": "uuid",
    "org_name": "Acme Organization",
    "role_id": "uuid",
    "role_name": "Administrator"
  }
}
```

### JWT Payload Structure

```json
{
  "sub": "user-uuid",
  "org_id": "org-uuid",
  "role_id": "role-uuid",
  "iat": 1707321600,
  "exp": 1707580800,
  "type": "session"
}
```

| Field | Description |
|-------|-------------|
| `sub` | User ID (subject) |
| `org_id` | Organization/tenant ID |
| `role_id` | User's role (Client vs Administrator) |
| `iat` | Issued at timestamp |
| `exp` | Expiration timestamp |
| `type` | Always `"session"` for JWT tokens |

### Password Verification

Passwords are hashed using bcrypt:

```python
import bcrypt

# Verification
password_valid = bcrypt.checkpw(
    password.encode("utf-8"),
    stored_hash.encode("utf-8"),
)
```

### Get Current User

```
GET /api/auth/me
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name_f": "John",
  "name_l": "Doe",
  "name": "John Doe",
  "company": "Acme Inc",
  "phone": "+1234567890",
  "org_id": "uuid",
  "org_name": "Acme Organization",
  "role_id": "uuid",
  "role_name": "Administrator",
  "status": 1
}
```

---

## 4. API Tokens

API tokens are used for machine-to-machine integrations (webhooks, external services, scripts).

### Token Format

```
sengx_<48-character-random-string>
```

Example: `sengx_Abc123XyzDef456GhiJkl789MnoPqr012StuVwx345`

### How API Tokens Work

1. **Generation**: A random token is generated with `secrets.token_urlsafe(36)`
2. **Storage**: Only the SHA-256 hash is stored in the database
3. **Validation**: Incoming tokens are hashed and compared against stored hashes

```python
from hashlib import sha256

# Hash for storage
token_hash = sha256(plaintext_token.encode()).hexdigest()

# Validation
incoming_hash = sha256(incoming_token.encode()).hexdigest()
# Compare incoming_hash against stored token_hash
```

### Generating API Tokens

Use the provided script:

```bash
python scripts/generate_token.py
```

Or programmatically:

```python
import secrets
from hashlib import sha256

# Generate token
plaintext_token = f"sengx_{secrets.token_urlsafe(36)}"

# Hash for storage
token_hash = sha256(plaintext_token.encode()).hexdigest()

# Store in database
supabase.table("api_tokens").insert({
    "user_id": user_id,
    "org_id": org_id,
    "name": "My Integration Token",
    "token_hash": token_hash,
    "expires_at": None,  # Or a timestamp
}).execute()

# Give plaintext_token to the user (cannot be recovered)
print(f"Your token: {plaintext_token}")
```

### Token Expiration

- Tokens can have an optional `expires_at` timestamp
- If `expires_at` is null, the token never expires
- Expired tokens return 401 Unauthorized

### Token Usage Tracking

Each API token tracks `last_used_at`, updated on every successful authentication.

---

## 5. Auth Dependencies

The `app/auth/` module provides three FastAPI dependencies:

### AuthContext

```python
@dataclass
class AuthContext:
    """Authentication context containing org and user info."""
    org_id: str
    user_id: str
    token_id: str | None = None
    auth_method: str = "api_token"  # "api_token" or "session"
```

### get_current_org()

**API tokens only.** Use for machine-to-machine endpoints.

```python
from app.auth import AuthContext, get_current_org

@router.get("/api/resources")
async def list_resources(auth: AuthContext = Depends(get_current_org)):
    # auth.org_id is guaranteed to be set
    ...
```

### get_current_user()

**JWT sessions only.** Use for endpoints that require a logged-in user (customer portal).

```python
from app.auth import AuthContext, get_current_user

@router.get("/api/auth/me")
async def me(auth: AuthContext = Depends(get_current_user)):
    # auth.user_id is a logged-in user
    ...
```

### get_current_auth()

**Dual auth.** Accepts either JWT or API token. Tries JWT first (no DB call), falls back to API token.

```python
from app.auth import AuthContext, get_current_auth

@router.get("/api/orders")
async def list_orders(auth: AuthContext = Depends(get_current_auth)):
    # Works with either auth method
    ...
```

### Choosing the Right Dependency

| Dependency | JWT Session | API Token | Use Case |
|------------|-------------|-----------|----------|
| `get_current_org` | No | Yes | Webhooks, external integrations |
| `get_current_user` | Yes | No | User portal, requires active session |
| `get_current_auth` | Yes | Yes | Most API endpoints |

---

## 6. Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET_KEY` | `"change-me-in-production"` | Secret key for signing JWTs |
| `JWT_ALGORITHM` | `"HS256"` | JWT signing algorithm |
| `JWT_EXPIRATION_HOURS` | `72` | Token expiration time |

### Settings Class

```python
# app/config.py
class Settings(BaseSettings):
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 72
```

### Security Notes

- **Always** set a strong `JWT_SECRET_KEY` in production
- The default key is intentionally obvious to prevent accidental use
- Rotate keys periodically and have a key rotation strategy

---

## 7. Database Schema

### users Table

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255),          -- bcrypt hash
  name_f VARCHAR(100),
  name_l VARCHAR(100),
  role_id UUID REFERENCES roles(id),
  status INTEGER DEFAULT 1,            -- 0 = disabled, 1 = active
  ...
);
```

### api_tokens Table

```sql
CREATE TABLE api_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  org_id UUID NOT NULL REFERENCES organizations(id),
  name VARCHAR(255),                   -- Human-readable name
  token_hash VARCHAR(64) NOT NULL,     -- SHA-256 hash (64 hex chars)
  expires_at TIMESTAMPTZ,              -- NULL = never expires
  last_used_at TIMESTAMPTZ,            -- Updated on each use
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_api_tokens_token_hash ON api_tokens(token_hash);
CREATE INDEX idx_api_tokens_org_id ON api_tokens(org_id);
```

---

## 8. Usage Examples

### cURL: Login and Use Token

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret123"}' \
  | jq -r '.token')

# Use token
curl http://localhost:8000/api/clients \
  -H "Authorization: Bearer $TOKEN"
```

### cURL: Use API Token

```bash
# API token (stored in environment)
curl http://localhost:8000/api/orders \
  -H "Authorization: Bearer $API_TOKEN"
```

### Python: Login Flow

```python
import httpx

# Login
response = httpx.post("http://localhost:8000/api/auth/login", json={
    "email": "user@example.com",
    "password": "secret123",
})
token = response.json()["token"]

# Authenticated request
response = httpx.get(
    "http://localhost:8000/api/clients",
    headers={"Authorization": f"Bearer {token}"},
)
clients = response.json()
```

### JavaScript: Login Flow

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'secret123',
  }),
});
const { token } = await loginResponse.json();

// Authenticated request
const response = await fetch('http://localhost:8000/api/clients', {
  headers: { Authorization: `Bearer ${token}` },
});
const clients = await response.json();
```

---

## Summary

| Component | Location | Purpose |
|-----------|----------|---------|
| `app/auth/__init__.py` | Module exports | Public API: `AuthContext`, `get_current_*` |
| `app/auth/dependencies.py` | Auth dependencies | FastAPI dependencies, token validation |
| `app/auth/jwt.py` | JWT handling | Create and decode JWTs |
| `app/auth/utils.py` | Utilities | Token hashing, bearer extraction |
| `app/routers/auth.py` | Auth endpoints | `/api/auth/login`, `/api/auth/me` |
| `app/config.py` | Configuration | JWT settings |
| `scripts/generate_token.py` | Token generator | Create API tokens |
