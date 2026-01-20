# Update Client

```
PUT /api/clients/{id}
```

---

## 1. Purpose

Updates a client by setting the values of the parameters passed. Parameters not provided are left unchanged.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated operator.

---

## 3. Request Parameters

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | **Yes** | Client identifier. |

### Request Headers

| Header | Type | Required |
|--------|------|----------|
| `Authorization` | string | Yes |
| `Content-Type` | string | Yes (`application/json`) |
| `Accept` | string | Yes (`application/json`) |
| `X-Api-Version` | string | No |

### Request Body

All fields are optional. Only provided fields are updated.

```json
{
  "name_f": "John",
  "name_l": "Doe",
  "email": "updated@example.com",
  "company": "New Company Inc.",
  "phone": "555-9999",
  "tax_id": "987654321",
  "address": {
    "line_1": "456 Oak Ave",
    "line_2": null,
    "city": "Los Angeles",
    "state": "CA",
    "country": "US",
    "postcode": "90001"
  },
  "note": "Updated notes",
  "optin": "No",
  "stripe_id": "cus_yyy",
  "custom_fields": { "industry": "Finance" },
  "status_id": 1
}
```

### Field Definitions (Request)

| Field | Writable | Type | Required | Description |
|-------|----------|------|----------|-------------|
| `name_f` | Yes | string | No | First name. |
| `name_l` | Yes | string | No | Last name. |
| `email` | Yes | string | No | Email address. Must be unique. |
| `company` | Yes | string | No | Company name. |
| `phone` | Yes | string | No | Phone number. |
| `tax_id` | Yes | string | No | Tax identifier. |
| `address` | Yes | object \| null | No | Billing address. See Address Handling. |
| `note` | Yes | string | No | Internal note. |
| `optin` | Yes | string | No | Marketing opt-in. |
| `stripe_id` | Yes | string | No | Stripe customer ID. |
| `custom_fields` | Yes | object | No | Custom field values. **Replaces entire object.** |
| `status_id` | Yes | integer | No | Account status. |
| `created_at` | Yes | datetime | No | Override creation timestamp. |

### Address Object (Request)

| Field | Type | Description |
|-------|------|-------------|
| `line_1` | string \| null | Street address line 1. |
| `line_2` | string \| null | Street address line 2. |
| `city` | string \| null | City. |
| `state` | string \| null | State/Province. |
| `country` | string \| null | ISO 3166-1 alpha-2 code. |
| `postcode` | string \| null | Postal code. |

### Write-Time Ignored Fields

These fields are **silently ignored** if provided in the request body:

| Field | Reason |
|-------|--------|
| `id` | Immutable. |
| `name` | Computed field. |
| `balance` | Managed via invoices. Use invoice endpoints. |
| `spent` | Computed field. |
| `aff_id` | Immutable after creation. |
| `aff_link` | Immutable after creation. |
| `role_id` | Forced to client role. |
| `role` | Joined object. |
| `ga_cid` | Set via tracking. |

### Write-Time Restricted Fields

| Field | Behavior |
|-------|----------|
| `email` | Must be unique (excluding current client). Returns 400 if duplicate. |
| `status_id` | Must be valid status integer. |

---

## 4. Side Effects

| Effect | Condition | Description |
|--------|-----------|-------------|
| **Address created** | `address` provided, client has no existing address | New address record created and linked. |
| **Address updated** | `address` provided, client has existing address | Existing address record updated. |
| **Address cleared** | `address: null` explicitly sent | `address_id` set to null. Address record remains (orphaned). |
| **Address unchanged** | `address` field omitted from request | No change to address. |

---

## 5. Response Shape

### 200 OK

Returns the updated client object.

```json
{
  "id": "uuid",
  "name": "John Doe",
  "name_f": "John",
  "name_l": "Doe",
  "email": "updated@example.com",
  "company": "New Company Inc.",
  "phone": "555-9999",
  "tax_id": "987654321",
  "address": {
    "line_1": "456 Oak Ave",
    "line_2": null,
    "city": "Los Angeles",
    "state": "CA",
    "country": "US",
    "postcode": "90001",
    "name_f": "John",
    "name_l": "Doe",
    "tax_id": "987654321",
    "company_name": "New Company Inc.",
    "company_vat": null
  },
  "note": "Updated notes",
  "balance": "100.00",
  "spent": "500.00",
  "optin": "No",
  "stripe_id": "cus_yyy",
  "custom_fields": { "industry": "Finance" },
  "status": 1,
  "aff_id": 12345,
  "aff_link": "https://example.com/r/ABC123",
  "role_id": "uuid",
  "role": { ... },
  "ga_cid": "123456789.1234567890",
  "created_at": "2024-01-15T10:30:00+00:00"
}
```

### Response Structure

| Field | Type | Present | Description |
|-------|------|---------|-------------|
| `id` | UUID | Always | Client identifier. |
| `name` | string | Always | Computed: `name_f + " " + name_l`. |
| `name_f` | string | Always | First name. |
| `name_l` | string | Always | Last name. |
| `email` | string | Always | Email address. |
| `company` | string \| null | Always | Company name. |
| `phone` | string \| null | Always | Phone number. |
| `tax_id` | string \| null | Always | Tax identifier. |
| `address` | AddressObject \| null | Always | Joined address or `null`. |
| `note` | string \| null | Always | Internal note. |
| `balance` | string | Always | Account credit balance. |
| `spent` | string \| null | Always | Computed sum of paid invoices. |
| `optin` | string \| null | Always | Marketing opt-in. |
| `stripe_id` | string \| null | Always | Stripe customer ID. |
| `custom_fields` | object | Always | Custom fields. |
| `status` | integer | Always | Account status. |
| `aff_id` | integer | Always | Affiliate ID. |
| `aff_link` | string | Always | Affiliate link. |
| `role_id` | UUID | Always | Role identifier. |
| `role` | RoleObject | Always | Joined role. |
| `ga_cid` | string \| null | Always | Google Analytics client ID. |
| `created_at` | datetime | Always | Creation timestamp. |

---

## 6. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | Immutable identifier. |
| `name` | Computed | Derived at response time. |
| `name_f` | Read + Write | Updatable. |
| `name_l` | Read + Write | Updatable. |
| `email` | Read + Write | Must remain unique. |
| `company` | Read + Write | Updatable. |
| `phone` | Read + Write | Updatable. |
| `tax_id` | Read + Write | Updatable. |
| `address` | Read + Write | See Address Handling. |
| `note` | Read + Write | Updatable. |
| `balance` | Read-only | Cannot be set directly. Use invoices. |
| `spent` | Computed | Derived at response time. |
| `optin` | Read + Write | Updatable. |
| `stripe_id` | Read + Write | Updatable. |
| `custom_fields` | Read + Write | **Full replacement.** Not merged. |
| `status` / `status_id` | Read + Write | Request: `status_id`. Response: `status`. |
| `aff_id` | Read-only | Immutable. |
| `aff_link` | Read-only | Immutable. |
| `role_id` | Read-only | Forced to client role. |
| `role` | Read-only (joined) | Embedded role. |
| `ga_cid` | Read-only | Set via tracking. |
| `created_at` | Read + Write | Can be overridden. |

---

## 7. Error Behavior

### 400 Bad Request — Validation Error

Invalid field values.

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "email": ["The email must be a valid email address."]
  }
}
```

### 400 Bad Request — Uniqueness Violation

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "email": ["The email has already been taken."]
  }
}
```

**Cause:** Email matches another client (not the current one).

### 401 Unauthorized

Missing or invalid Bearer token.

```json
{
  "error": "Unauthorized"
}
```

### 404 Not Found

Client does not exist.

```json
{
  "error": "Not Found"
}
```

---

## 8. Notes / Edge Cases

### Partial Updates

Only provided fields are updated. Omitted fields retain their current values.

```json
// Updates only company, leaves everything else unchanged
{ "company": "New Company Name" }
```

### Address Handling

| Request Payload | Behavior |
|-----------------|----------|
| `address` omitted | Address unchanged. |
| `address: null` | Clears `address_id`. Client will have no linked address. |
| `address: {}` | Updates existing address to all nulls, or creates empty address. |
| `address: { line_1: "..." }` | Updates/creates address with specified fields. Unspecified fields set to `null`. |

**Critical:** Address updates are **full replacements**, not merges. If you send `{ line_1: "New St" }`, all other address fields become `null`.

To update a single address field while preserving others, include all address fields in the request.

### custom_fields Replacement

The `custom_fields` object is **fully replaced**, not merged.

```json
// Before: { "industry": "Tech", "source": "Referral" }
// Request:
{ "custom_fields": { "industry": "Finance" } }
// After: { "industry": "Finance" }
// "source" is lost
```

To preserve existing custom fields, fetch the current values, merge locally, and send the complete object.

### Balance Field

`balance` cannot be set via update. Attempting to include `balance` in the request body is silently ignored.

To modify client balance:
- Create an invoice with credit items
- Mark invoices as paid
- Use dedicated balance adjustment endpoints (if available)

### Invoice Address Snapshots

Updating a client's address does **not** retroactively update existing invoices. Invoices store `billing_address` as a JSONB snapshot at creation time.
