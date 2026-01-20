# Create Client

## Endpoint

```
POST /api/clients
```

## Description

Creates a new client user account.

## Authentication

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

---

## Request

### Request Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer token |
| `Content-Type` | string | Yes | `application/json` |
| `Accept` | string | Yes | `application/json` |
| `X-Api-Version` | string | No | API version identifier |

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
  "balance": "100.00",
  "optin": "Yes",
  "stripe_id": "cus_xxx",
  "custom_fields": {},
  "status_id": 1,
  "created_at": "2024-01-15T10:30:00+00:00"
}
```

### Body Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name_f` | string | Yes | First name |
| `name_l` | string | Yes | Last name |
| `email` | string | Yes | Email address (must be unique) |
| `company` | string | No | Company name |
| `phone` | string | No | Phone number |
| `tax_id` | string | No | Tax identifier |
| `address` | object | No | Billing address |
| `note` | string | No | Internal note |
| `balance` | number | No | Initial account balance. Default: `0.00` |
| `optin` | string | No | Marketing opt-in status |
| `stripe_id` | string | No | Stripe customer ID |
| `custom_fields` | object | No | Custom field values |
| `status_id` | integer | No | Account status. Default: `1` |
| `created_at` | string (datetime) | No | Override creation timestamp |

### Address Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `line_1` | string | No | Street address line 1 |
| `line_2` | string | No | Street address line 2 |
| `city` | string | No | City |
| `state` | string | No | State/Province |
| `country` | string | No | ISO 3166-1 alpha-2 country code |
| `postcode` | string | No | Postal/ZIP code |

---

## Validation Rules

| Field | Rules |
|-------|-------|
| `email` | Required, valid email format, unique |
| `name_f` | Required, string |
| `name_l` | Required, string |
| `balance` | Numeric, >= 0 |
| `status_id` | Integer |
| `address.country` | ISO 3166-1 alpha-2 code |

---

## Response

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
  "balance": "100.00",
  "spent": null,
  "optin": "Yes",
  "stripe_id": "cus_xxx",
  "custom_fields": {},
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
  "ga_cid": null,
  "created_at": "2024-01-15T10:30:00+00:00"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string (UUID) | Unique client identifier |
| `name` | string | Full name (computed) |
| `name_f` | string | First name |
| `name_l` | string | Last name |
| `email` | string | Email address |
| `company` | string | Company name |
| `phone` | string | Phone number |
| `tax_id` | string | Tax identifier |
| `address` | object | Billing address |
| `note` | string | Internal note |
| `balance` | string | Account balance |
| `spent` | string \| null | Total amount spent |
| `optin` | string | Marketing opt-in status |
| `stripe_id` | string | Stripe customer ID |
| `custom_fields` | object | Custom field values |
| `status` | integer | Account status |
| `aff_id` | integer | Auto-generated affiliate ID |
| `aff_link` | string | Auto-generated affiliate link |
| `role_id` | string (UUID) | Role identifier |
| `role` | object | Embedded role object |
| `ga_cid` | string \| null | Google Analytics client ID |
| `created_at` | string (datetime) | Creation timestamp |

---

## Error Responses

### 400 Bad Request

Invalid request body or validation failure.

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "email": ["The email field is required."],
    "name_f": ["The name_f field is required."]
  }
}
```

### 401 Unauthorized

Missing or invalid authentication token.

```json
{
  "error": "Unauthorized"
}
```

---

## Notes

- Email addresses must be unique across all clients
- A client role is automatically assigned to new clients
- The `aff_id` and `aff_link` are auto-generated
- The `spent` field is computed and starts as `null`
- If `address` is provided, a separate address record is created and linked
- The `name` response field is computed from `name_f` and `name_l`
