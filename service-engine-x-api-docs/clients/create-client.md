# Create Client

```
POST /api/clients
```

---

## 1. Purpose

Creates a new client user account.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated operator.

---

## 3. Request Parameters

### Request Headers

| Header | Type | Required |
|--------|------|----------|
| `Authorization` | string | Yes |
| `Content-Type` | string | Yes (`application/json`) |
| `Accept` | string | Yes (`application/json`) |
| `X-Api-Version` | string | No |

### Request Body

```json
{
  "name_f": "John",
  "name_l": "Doe",
  "email": "client@example.com",
  "company": "Acme Inc.",
  "phone": "555-1234",
  "tax_id": "123456789",
  "address": {
    "line_1": "123 Main St",
    "line_2": "Suite 100",
    "city": "New York",
    "state": "NY",
    "country": "US",
    "postcode": "10001"
  },
  "note": "VIP client",
  "optin": "Yes",
  "stripe_id": "cus_xxx",
  "custom_fields": { "industry": "Technology" },
  "status_id": 1,
  "created_at": "2024-01-15T10:30:00+00:00"
}
```

### Field Definitions (Request)

| Field | Writable | Type | Required | Default | Description |
|-------|----------|------|----------|---------|-------------|
| `name_f` | Yes | string | **Yes** | — | First name. |
| `name_l` | Yes | string | **Yes** | — | Last name. |
| `email` | Yes | string | **Yes** | — | Email address. Must be unique. |
| `company` | Yes | string | No | `null` | Company name. |
| `phone` | Yes | string | No | `null` | Phone number. |
| `tax_id` | Yes | string | No | `null` | Tax identifier. |
| `address` | Yes | object | No | `null` | Billing address. See Address Handling. |
| `note` | Yes | string | No | `null` | Internal note. |
| `optin` | Yes | string | No | `null` | Marketing opt-in. |
| `stripe_id` | Yes | string | No | `null` | Stripe customer ID. |
| `custom_fields` | Yes | object | No | `{}` | Custom field key-values. |
| `status_id` | Yes | integer | No | `1` | Account status. |
| `created_at` | Yes | datetime | No | `now()` | Override creation timestamp. |

### Address Object (Request)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `line_1` | string | No | Street address line 1. |
| `line_2` | string | No | Street address line 2. |
| `city` | string | No | City. |
| `state` | string | No | State/Province. |
| `country` | string | No | ISO 3166-1 alpha-2 code (e.g., `US`, `GB`). |
| `postcode` | string | No | Postal/ZIP code. |

### Write-Time Ignored Fields

These fields are **silently ignored** if provided in the request body:

| Field | Reason |
|-------|--------|
| `id` | Auto-generated UUID. |
| `name` | Computed from `name_f` + `name_l`. |
| `balance` | Managed via invoices. Starts at `0.00`. |
| `spent` | Computed from paid invoices. |
| `aff_id` | Auto-generated. |
| `aff_link` | Auto-generated. |
| `role_id` | Forced to client role. |
| `role` | Joined object, not writable. |
| `ga_cid` | Set via tracking, not API. |

### Write-Time Restricted Fields

| Field | Behavior |
|-------|----------|
| `email` | Must be unique. Returns 400 if duplicate. |
| `status_id` | Must be valid status integer. |

---

## 4. Side Effects

| Effect | Description |
|--------|-------------|
| **Address record created** | If `address` object provided, a new row is inserted into `addresses` table and linked to user via `address_id`. |
| **Affiliate ID generated** | `aff_id` and `aff_link` auto-generated for new client. |
| **Role assigned** | Client role automatically assigned via `role_id`. |

---

## 5. Response Shape

### 201 Created

Returns the created client object.

```json
{
  "id": "uuid",
  "name": "John Doe",
  "name_f": "John",
  "name_l": "Doe",
  "email": "client@example.com",
  "company": "Acme Inc.",
  "phone": "555-1234",
  "tax_id": "123456789",
  "address": {
    "line_1": "123 Main St",
    "line_2": "Suite 100",
    "city": "New York",
    "state": "NY",
    "country": "US",
    "postcode": "10001",
    "name_f": "John",
    "name_l": "Doe",
    "tax_id": "123456789",
    "company_name": null,
    "company_vat": null
  },
  "note": "VIP client",
  "balance": "0.00",
  "spent": null,
  "optin": "Yes",
  "stripe_id": "cus_xxx",
  "custom_fields": { "industry": "Technology" },
  "status": 1,
  "aff_id": 12345,
  "aff_link": "https://example.com/r/ABC123",
  "role_id": "uuid",
  "role": { ... },
  "ga_cid": null,
  "created_at": "2024-01-15T10:30:00+00:00"
}
```

### Response Structure

| Field | Type | Present | Description |
|-------|------|---------|-------------|
| `id` | UUID | Always | Generated identifier. |
| `name` | string | Always | Computed: `name_f + " " + name_l`. |
| `name_f` | string | Always | First name. |
| `name_l` | string | Always | Last name. |
| `email` | string | Always | Email address. |
| `company` | string \| null | Always | Company name. |
| `phone` | string \| null | Always | Phone number. |
| `tax_id` | string \| null | Always | Tax identifier. |
| `address` | object \| null | Always | `null` if not provided; otherwise AddressObject. |
| `note` | string \| null | Always | Internal note. |
| `balance` | string | Always | Starts at `"0.00"`. |
| `spent` | string \| null | Always | `null` for new clients. |
| `optin` | string \| null | Always | Marketing opt-in. |
| `stripe_id` | string \| null | Always | Stripe customer ID. |
| `custom_fields` | object | Always | Custom fields. Default `{}`. |
| `status` | integer | Always | Account status. |
| `aff_id` | integer | Always | Auto-generated affiliate ID. |
| `aff_link` | string | Always | Auto-generated affiliate link. |
| `role_id` | UUID | Always | Client role ID. |
| `role` | object | Always | Joined RoleObject. |
| `ga_cid` | string \| null | Always | `null` for new clients. |
| `created_at` | datetime | Always | Creation timestamp. |

### AddressObject (Response)

When address is provided, response includes expanded address with additional fields:

| Field | Type | Description |
|-------|------|-------------|
| `line_1` | string \| null | Street address line 1. |
| `line_2` | string \| null | Street address line 2. |
| `city` | string \| null | City. |
| `state` | string \| null | State/Province. |
| `country` | string \| null | Country code. |
| `postcode` | string \| null | Postal code. |
| `name_f` | string \| null | Recipient first name (inherited from user if not set). |
| `name_l` | string \| null | Recipient last name (inherited from user if not set). |
| `tax_id` | string \| null | Address-specific tax ID. |
| `company_name` | string \| null | Address-specific company name. |
| `company_vat` | string \| null | VAT number. |

---

## 6. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | Auto-generated UUID. |
| `name` | Computed | Derived at response time. Never stored. |
| `name_f` | Read + Write | Required on create. |
| `name_l` | Read + Write | Required on create. |
| `email` | Read + Write | Required. Must be unique. |
| `company` | Read + Write | Optional. |
| `phone` | Read + Write | Optional. |
| `tax_id` | Read + Write | Optional. |
| `address` | Read + Write | Creates linked address record. See Address Handling. |
| `note` | Read + Write | Optional. |
| `balance` | Read-only | Managed via invoices. Cannot be set on create. |
| `spent` | Computed | Sum of paid invoices. Always `null` on create. |
| `optin` | Read + Write | Optional. |
| `stripe_id` | Read + Write | Optional. |
| `custom_fields` | Read + Write | Optional. Defaults to `{}`. |
| `status` / `status_id` | Read + Write | Request uses `status_id`, response uses `status`. |
| `aff_id` | Read-only | Auto-generated. |
| `aff_link` | Read-only | Auto-generated. |
| `role_id` | Read-only | Forced to client role. |
| `role` | Read-only (joined) | Client role object. |
| `ga_cid` | Read-only | Set via tracking. |
| `created_at` | Read + Write | Can be overridden on create. |

---

## 7. Error Behavior

### 400 Bad Request — Validation Error

Invalid or missing required fields.

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "email": ["The email field is required."],
    "name_f": ["The name_f field is required."]
  }
}
```

**Causes:**
- Missing `email`, `name_f`, or `name_l`
- Invalid email format
- Invalid `status_id` value

### 400 Bad Request — Uniqueness Violation

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "email": ["The email has already been taken."]
  }
}
```

**Cause:** Email already exists for another client.

### 401 Unauthorized

Missing or invalid Bearer token.

```json
{
  "error": "Unauthorized"
}
```

---

## 8. Notes / Edge Cases

### Address Handling

| Scenario | Behavior |
|----------|----------|
| `address` omitted | No address record created. Response `address` is `null`. |
| `address: null` | Explicit null. No address record created. Response `address` is `null`. |
| `address: {}` | Empty object. Address record created with all fields `null`. |
| `address: { line_1: "..." }` | Address record created with provided fields. Missing fields are `null`. |

**Important:** The address is stored as a separate record in the `addresses` table, linked via `users.address_id`. This is a **live reference**, not a snapshot. Changes to the address record affect the client's address.

**Invoice addresses are different:** Invoices store `billing_address` as a **JSONB snapshot** at invoice creation time. Updating a client's address does not affect existing invoices.

### Computed Fields

- `name`: Concatenation of `name_f` and `name_l` with space. Computed at response time.
- `spent`: Sum of `total` from all paid invoices for this client. Computed at response time. `null` if no paid invoices.

### Auto-Generated Fields

- `id`: UUID generated via `gen_random_uuid()`.
- `aff_id`: Integer auto-generated.
- `aff_link`: URL constructed from `aff_id`.

### Role Assignment

All clients are assigned the client role (identified by `dashboard_access = 0`). The `role_id` field in the request is ignored. Attempting to create a client with a team role will fail or be overridden.
