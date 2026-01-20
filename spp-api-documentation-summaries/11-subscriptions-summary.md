# 11. Subscriptions - API Documentation Summary

## Overview
The Subscriptions API provides read and update access to recurring subscriptions. Subscriptions are automatically created when orders for recurring services are placed.

**Note:** No create or delete endpoints exist - subscriptions are managed through orders.

---

## 11.1 List All Subscriptions

### File Path
`spp-api-documentation/11. Subscriptions/11.1 list-subscriptions.md`

### Name
List all subscriptions

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/subscriptions`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Request Headers
| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| Authorization | string | required | Bearer token | `Bearer 123` |
| X-Api-Version | string | optional | API version identifier | `2024-03-05` |

### Query Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| limit | integer | optional | Items per page | `10` |
| page | integer | optional | Page number | `1` |
| sort | string | optional | Sort by fields | `id:desc` |
| filters[user_id][$in][] | array[integer] | optional | Filter by user IDs | |

**Supported Filter Operators:** `$eq` (=), `$lt` (<), `$gt` (>), `$in` (in array)

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

### Response Body Schema (200)
```json
{
  "data": [Subscription],
  "links": PaginationLinks,
  "meta": PaginationMeta
}
```

#### Subscription Object
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| id | integer | required | Subscription ID | `1` |
| number | string | optional | Subscription number | `E4A269FC` |
| invoice_id | string | required | Invoice ID (legacy) | `E4A269FC` |
| status | string | required | Subscription status | `Active` |
| processor_id | string | required | External processor ID (Stripe) | `123456789` |
| current_period_end | string\<date-time\> | required | Current billing period end | `2021-08-31T14:48:00+00:00` |
| payments | array[object] | required | Payment history | |
| orders | array[string] | required | Associated order numbers | `["E4A269FC"]` |
| payment_count | integer | required | Total payments made | `3` |
| client | User | required | Client user object | |

#### Payment Object (in payments array)
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| invoice_id | integer | Invoice ID | `1` |
| created_at | string\<date-time\> | Payment date | `2021-08-31T14:48:00+00:00` |
| amount | string | Payment amount | `10.00` |
| paysys | string | Payment system | `Stripe` |

### Example Request
```bash
curl --request GET \
  --url https://example.spp.co/api/subscriptions \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123'
```

### Notes / Gotchas
- Subscriptions sorted by creation date in descending order
- `invoice_id` is marked as legacy - use `number` instead
- `processor_id` is the Stripe subscription ID

---

## 11.2 Retrieve a Subscription

### File Path
`spp-api-documentation/11. Subscriptions/11.2 retrieve-subscription.md`

### Name
Retrieve a subscription

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/subscriptions/{subscription}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| subscription | integer or allOf | **required** | Subscription ID | `10` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |

### Response Body Schema (200)
Returns `Subscription` object (see 11.1 for schema)

### Example Request
```bash
curl --request GET \
  --url https://example.spp.co/api/subscriptions/10 \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123'
```

---

## 11.3 Update a Subscription

### File Path
`spp-api-documentation/11. Subscriptions/11.3 update-subscription.md`

### Name
Update a subscription

### HTTP Method
`PUT`

### URL Path
`https://{workspaceUrl}/api/subscriptions/{subscription}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| subscription | integer or allOf | **required** | Subscription ID | `10` |

### Request Body Schema
| Field | Type | Required | Allowed Values | Description | Example |
|-------|------|----------|----------------|-------------|---------|
| status | integer | optional | `0`, `1`, `2`, `3`, `4` | New status | `1` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid status value |
| 401 | Unauthorized |
| 404 | Not Found |

### Response Body Schema (200)
Returns updated `Subscription` object (see 11.1 for schema)

### Example Request
```bash
curl --request PUT \
  --url https://example.spp.co/api/subscriptions/10 \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'Content-Type: application/json' \
  --data '{"status": 1}'
```

### Side Effects / State Changes
- Updates subscription status
- May trigger notifications
- May affect billing in external processor

### Notes / Gotchas
- Only `status` can be updated
- Status is integer in request, string in response
- Status values 0-4 allowed but not documented

---

## Subscription Status Values

The documentation lists allowed status values as `0`, `1`, `2`, `3`, `4` but does not map them to status names. Based on common patterns:

| Value | Likely Status |
|-------|---------------|
| 0 | Inactive/Canceled |
| 1 | Active |
| 2 | Paused |
| 3 | Past Due |
| 4 | Expired |

**Note:** These are assumptions - actual values not documented.

---

## Ambiguities and Missing Information

1. **Status Values:** Integer status values (0-4) not mapped to string names
2. **No Create Endpoint:** Subscriptions created through orders only
3. **No Delete/Cancel Endpoint:** How to cancel subscriptions not documented
4. **Stripe Integration:** How `processor_id` maps to Stripe subscriptions not documented
5. **Payment History:** How payments array is populated not documented
6. **Orders Array:** Contains order numbers (strings), not IDs

---

## Cross-references

- Orders (7. Orders) - Subscriptions created via recurring orders
- Invoices (4. Invoices) - Payments reference invoices
- Services (10. Services) - Recurring services create subscriptions
- Clients (17. Clients) - `client` object
