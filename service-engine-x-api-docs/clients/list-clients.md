# List Clients

## Endpoint

```
GET /api/clients
```

## Description

Returns a paginated list of client users sorted by creation date in descending order.

## Authentication

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

---

## Request

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Items per page. Default: `20` |
| `page` | integer | No | Page number. Default: `1` |
| `sort` | string | No | Sort field and direction. Example: `id:desc` |
| `expand[]` | array[string] | No | Related objects to include in response |
| `filters[{field}][{operator}]` | varies | No | Filter results by field values |

### Supported Filter Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `$eq` | Equals | `filters[status][$eq]=1` |
| `$lt` | Less than | `filters[balance][$lt]=100` |
| `$gt` | Greater than | `filters[balance][$gt]=0` |
| `$in[]` | In array | `filters[id][$in][]=1&filters[id][$in][]=2` |

### Request Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer token |
| `Accept` | string | Yes | `application/json` |
| `X-Api-Version` | string | No | API version identifier |

---

## Response

### 200 OK

Returns a paginated collection of client objects.

```json
{
  "data": [
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
      "created_at": "2024-01-15T10:30:00+00:00"
    }
  ],
  "links": {
    "first": "https://example.com/api/clients?page=1",
    "last": "https://example.com/api/clients?page=5",
    "prev": null,
    "next": "https://example.com/api/clients?page=2"
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 5,
    "per_page": 20,
    "to": 20,
    "total": 100,
    "path": "https://example.com/api/clients",
    "links": [
      { "url": null, "label": "Previous", "active": false },
      { "url": "https://example.com/api/clients?page=1", "label": "1", "active": true },
      { "url": "https://example.com/api/clients?page=2", "label": "2", "active": false },
      { "url": "https://example.com/api/clients?page=2", "label": "Next", "active": false }
    ]
  }
}
```

### Response Fields

#### Client Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string (UUID) | Unique client identifier |
| `name` | string | Full name (computed: `name_f + name_l`) |
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
| `aff_id` | integer | Affiliate ID |
| `aff_link` | string | Affiliate referral link |
| `role_id` | string (UUID) | Role identifier |
| `role` | object | Embedded role object |
| `created_at` | string (datetime) | Creation timestamp |

#### Address Object

| Field | Type | Description |
|-------|------|-------------|
| `line_1` | string | Street address line 1 |
| `line_2` | string | Street address line 2 |
| `city` | string | City |
| `state` | string | State/Province |
| `country` | string | ISO 3166-1 alpha-2 country code |
| `postcode` | string | Postal/ZIP code |
| `name_f` | string | Recipient first name |
| `name_l` | string | Recipient last name |
| `tax_id` | string | Tax ID for billing |
| `company_name` | string | Company name for billing |
| `company_vat` | string | VAT number |

#### Pagination Links

| Field | Type | Description |
|-------|------|-------------|
| `first` | string | URL to first page |
| `last` | string | URL to last page |
| `prev` | string \| null | URL to previous page |
| `next` | string \| null | URL to next page |

#### Pagination Meta

| Field | Type | Description |
|-------|------|-------------|
| `current_page` | integer | Current page number |
| `from` | integer | First item index on current page |
| `to` | integer | Last item index on current page |
| `last_page` | integer | Total number of pages |
| `per_page` | integer | Items per page |
| `total` | integer | Total number of items |
| `path` | string | Base URL for pagination |
| `links` | array | Navigation link objects |

---

## Error Responses

### 401 Unauthorized

Missing or invalid authentication token.

```json
{
  "error": "Unauthorized"
}
```

---

## Notes

- Results are always sorted by `created_at` descending by default
- The `role` object is always included in the response
- The `name` field is a computed concatenation of `name_f` and `name_l`
- Filter operators can be combined for complex queries
- The `address` object may have null fields if not set
