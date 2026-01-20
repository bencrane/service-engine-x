# Retrieve Client

```
GET /api/clients/{id}
```

---

## 1. Purpose

Retrieves a single client by ID.

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
| `Accept` | string | Yes (`application/json`) |
| `X-Api-Version` | string | No |

---

## 4. Side Effects

None. Read-only operation.

---

## 5. Response Shape

### 200 OK

Returns the client object.

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
    "company_name": "Acme Inc.",
    "company_vat": "VAT123"
  },
  "note": "VIP client",
  "balance": "100.00",
  "spent": "500.00",
  "optin": "Yes",
  "stripe_id": "cus_xxx",
  "custom_fields": {
    "industry": "Technology",
    "source": "Referral"
  },
  "status": 1,
  "aff_id": 12345,
  "aff_link": "https://example.com/r/ABC123",
  "role_id": "uuid",
  "role": {
    "id": "uuid",
    "name": "Client",
    "dashboard_access": 0,
    "order_access": 1,
    "order_management": 0,
    "ticket_access": 1,
    "ticket_management": 0,
    "invoice_access": 1,
    "invoice_management": 0,
    "clients": 0,
    "services": 0,
    "coupons": 0,
    "forms": 0,
    "messaging": 1,
    "affiliates": 0,
    "settings_company": false,
    "settings_payments": false,
    "settings_team": false,
    "settings_modules": false,
    "settings_integrations": false,
    "settings_orders": false,
    "settings_tickets": false,
    "settings_accounts": false,
    "settings_messages": false,
    "settings_tags": false,
    "settings_sidebar": false,
    "settings_dashboard": false,
    "settings_templates": false,
    "settings_emails": false,
    "settings_language": false,
    "settings_logs": false,
    "created_at": "2024-01-01T00:00:00+00:00",
    "updated_at": "2024-01-01T00:00:00+00:00"
  },
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
| `address` | AddressObject \| null | Always | Joined address. `null` if no address linked. |
| `note` | string \| null | Always | Internal note. |
| `balance` | string | Always | Account credit balance. |
| `spent` | string \| null | Always | Computed sum of paid invoices. `null` if none. |
| `optin` | string \| null | Always | Marketing opt-in. |
| `stripe_id` | string \| null | Always | Stripe customer ID. |
| `custom_fields` | object | Always | Custom field values. `{}` if none. |
| `status` | integer | Always | Account status. |
| `aff_id` | integer | Always | Affiliate ID. |
| `aff_link` | string | Always | Affiliate referral link. |
| `role_id` | UUID | Always | Role identifier. |
| `role` | RoleObject | Always | Joined role. Never `null`. |
| `ga_cid` | string \| null | Always | Google Analytics client ID. |
| `created_at` | datetime | Always | Creation timestamp. |

### AddressObject (Joined, Optional)

Returns `null` if client has no linked address. Otherwise:

| Field | Type | Description |
|-------|------|-------------|
| `line_1` | string \| null | Street address line 1. |
| `line_2` | string \| null | Street address line 2. |
| `city` | string \| null | City. |
| `state` | string \| null | State/Province. |
| `country` | string \| null | ISO 3166-1 alpha-2 code. |
| `postcode` | string \| null | Postal code. |
| `name_f` | string \| null | Recipient first name. |
| `name_l` | string \| null | Recipient last name. |
| `tax_id` | string \| null | Address tax ID. |
| `company_name` | string \| null | Company name for billing. |
| `company_vat` | string \| null | VAT number. |

### RoleObject (Joined, Always Present)

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Role identifier. |
| `name` | string | Role name (e.g., "Client"). |
| `dashboard_access` | integer | 0 for clients. |
| `order_access` | integer | Order view permission level. |
| `order_management` | integer | Order edit permission level. |
| `ticket_access` | integer | Ticket view permission level. |
| `ticket_management` | integer | Ticket edit permission level. |
| `invoice_access` | integer | Invoice view permission level. |
| `invoice_management` | integer | Invoice edit permission level. |
| `clients` | integer | Client management permission. |
| `services` | integer | Service management permission. |
| `coupons` | integer | Coupon management permission. |
| `forms` | integer | Form management permission. |
| `messaging` | integer | Messaging permission. |
| `affiliates` | integer | Affiliate management permission. |
| `settings_*` | boolean | Various settings permissions. |
| `created_at` | datetime | Role creation timestamp. |
| `updated_at` | datetime | Role update timestamp. |

---

## 6. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | Primary identifier. |
| `name` | Computed | Derived from `name_f` + `name_l`. Never stored. |
| `name_f` | Read + Write | First name. |
| `name_l` | Read + Write | Last name. |
| `email` | Read + Write | Unique email. |
| `company` | Read + Write | Optional. |
| `phone` | Read + Write | Optional. |
| `tax_id` | Read + Write | Optional. |
| `address` | Read + Write | Joined from `addresses` table. Live reference. |
| `note` | Read + Write | Optional. |
| `balance` | Read-only | Modified via invoices/payments. |
| `spent` | Computed | Sum of paid invoice totals. Computed at response time. |
| `optin` | Read + Write | Optional. |
| `stripe_id` | Read + Write | Optional. |
| `custom_fields` | Read + Write | Defaults to `{}`. |
| `status` | Read + Write | Account status integer. |
| `aff_id` | Read-only | Auto-generated. |
| `aff_link` | Read-only | Auto-generated. |
| `role_id` | Read-only | Always client role. |
| `role` | Read-only (joined) | Embedded role object. |
| `ga_cid` | Read-only | Set via tracking. |
| `created_at` | Read + Write | Creation timestamp. |

---

## 7. Error Behavior

### 401 Unauthorized

Missing or invalid Bearer token.

```json
{
  "error": "Unauthorized"
}
```

### 404 Not Found

Client with specified ID does not exist.

```json
{
  "error": "Not Found"
}
```

**Causes:**
- Invalid UUID format
- UUID does not match any client

---

## 8. Notes / Edge Cases

### Address Behavior

The `address` field is a **live join** to the `addresses` table:
- If client has `address_id` set, the linked address is returned.
- If client has no `address_id`, response contains `"address": null`.
- Individual address fields may be `null` even when address object exists.

### Computed Fields

- `name`: Concatenation of `name_f` and `name_l`. Computed at response time.
- `spent`: Aggregate sum of `invoices.total` where `invoices.user_id = client.id` and invoice is paid. Computed at response time. Returns `null` if no paid invoices exist.

### Role Embedding

The `role` object is always joined and present. It is never `null`. For clients, `role.dashboard_access` is always `0`.
