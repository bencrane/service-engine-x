# 10. Services - API Documentation Summary

## Overview
The Services API provides full CRUD operations for managing services (products/offerings that can be ordered). Services define pricing models, recurring billing configurations, deadlines, and can be organized into folders.

---

## 10.1 List All Services

### File Path
`spp-api-documentation/10. Services/10.1 list-services.md`

### Name
List all services

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/services`

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
| filters[id][$in][] | array[integer] | optional | Filter by IDs | |

**Supported Filter Operators:** `$eq` (=), `$lt` (<), `$gt` (>), `$in` (in array)

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

### Response Body Schema (200)
```json
{
  "data": [Service],
  "links": PaginationLinks,
  "meta": PaginationMeta
}
```

#### Service Object
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| id | integer | required | Service ID | `1` |
| name | string | required | Service name | `Service name` |
| description | string | required | Description | `Service description` |
| image | string | required | Image URL | `https://example.com/image.png` |
| recurring | boolean | required | Is recurring | `true` |
| price | number | required | Base price | `1` |
| pretty_price | string | required | Formatted price | `$1.00` |
| currency | string | required | Currency code | `USD` |
| f_price | number | required | First payment price | `1` |
| f_period_l | integer | required | First period length | `1` |
| f_period_t | string | required | First period type | `day` |
| r_price | number | required | Recurring price | `1` |
| r_period_l | integer | required | Recurring period length | `1` |
| r_period_t | string | required | Recurring period type | `day` |
| recurring_action | string | required | Action on recurring | `Cancel` |
| multi_order | boolean | required | Allow multiple orders | `true` |
| request_orders | boolean | required | Request-based orders | `true` |
| option_categories | array[integer] | required | Option category IDs | `[1]` |
| option_variants | array[integer] | required | Option variant IDs | `[1]` |
| deadline | integer | required | Default deadline (days) | `1` |
| public | boolean | required | Publicly visible | `true` |
| sort_order | integer | required | Display order | `1` |
| braintree_plan_id | string | required | Braintree plan ID | |
| group_quantities | boolean | required | Group quantities | `true` |
| addon_to | array[integer] | required | Parent service IDs | `[1]` |
| folder_id | integer | required | Folder ID | `1` |
| metadata | object | required | Custom metadata | `{}` |
| hoth_product_key | string | required | HOTH product key | |
| hoth_package_name | string | required | HOTH package name | |
| created_at | string\<date-time\> | required | Created timestamp | |
| updated_at | string\<date-time\> | required | Updated timestamp | |
| provider_id | integer | required | Provider ID | `1` |
| provider_service_id | integer | required | Provider service ID | `1` |
| deleted_at | string\<date-time\> | required | Deleted timestamp | |
| media | array[object] | required | Media attachments | |

### Example Request
```bash
curl --request GET \
  --url https://example.spp.co/api/services \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123'
```

### Notes / Gotchas
- Services sorted by creation date in descending order
- `deleted_at` indicates soft-deleted services

---

## 10.2 Create a Service

### File Path
`spp-api-documentation/10. Services/10.2 create-service.md`

### Name
Create a service

### HTTP Method
`POST`

### URL Path
`https://{workspaceUrl}/api/services`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Request Headers
| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| Authorization | string | required | Bearer token | `Bearer 123` |
| X-Api-Version | string | optional | API version identifier | `2024-03-05` |
| Content-Type | string | required | Request format | `application/json` |

### Request Body Schema
| Field | Type | Required | Default | Description | Example |
|-------|------|----------|---------|-------------|---------|
| name | string | **required** | | Service name | `Service name` |
| recurring | integer | **required** | | Recurring type: 0=one-time, 1=recurring, 2=trial/setup fee | `1` |
| currency | string | **required** | | Currency code | `USD` |
| description | string | optional | | Description | `Service description` |
| price | number | optional | | Base price | `1` |
| f_price | number | optional | | First payment price | `1` |
| f_period_l | integer | optional | | First period length | `1` |
| f_period_t | string | optional | | First period type (D=day, W=week, M=month, Y=year) | `D` |
| r_price | number | optional | | Recurring price | `1` |
| r_period_l | integer | optional | | Recurring period length | `1` |
| r_period_t | string | optional | | Recurring period type | `D` |
| recurring_action | integer | optional | | Recurring action | `1` |
| deadline | integer | optional | | Default deadline in days | `1` |
| public | boolean | optional | `true` | Publicly visible | `true` |
| employees | array[integer] | optional | | Assigned employee IDs | `[1]` |
| group_quantities | boolean | optional | `false` | Group quantities | `true` |
| multi_order | integer | optional | | Allow multiple orders | `1` |
| request_orders | integer | optional | | Request-based orders | `1` |
| max_active_requests | integer | optional | | Max active requests | `1` |
| metadata | array[object] | optional | | Custom metadata | |
| parent_services | array[integer] | optional | | Parent service IDs (for addons) | `[1]` |
| clear_variants | boolean | optional | `false` | Clear existing variants | `true` |
| folder_id | integer | optional | | Folder ID | `1` |

#### Metadata Object
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | required | Metadata key |
| value | string | required | Metadata value |

### Response Status Codes
| Code | Description |
|------|-------------|
| 201 | Created |
| 400 | Bad Request - Validation error |
| 401 | Unauthorized |

### Response Body Schema (201)
Returns `Service` object (see 10.1 for schema)

### Example Request
```bash
curl --request POST \
  --url https://example.spp.co/api/services \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "Service name",
    "recurring": 1,
    "currency": "USD",
    "price": 100,
    "public": true
  }'
```

### Notes / Gotchas
- `recurring` is an integer in request but returns as boolean in response
- Period types: D=Day, W=Week, M=Month, Y=Year
- `f_` prefix = first payment, `r_` prefix = recurring payment

---

## 10.3 Retrieve a Service

### File Path
`spp-api-documentation/10. Services/10.3 retrieve-service.md`

### Name
Retrieve a service

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/services/{service}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| service | integer or allOf | **required** | Service ID | `1` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |

### Response Body Schema (200)
Returns `Service` object (see 10.1 for schema)

### Example Request
```bash
curl --request GET \
  --url https://example.spp.co/api/services/1 \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123'
```

---

## 10.4 Update a Service

### File Path
`spp-api-documentation/10. Services/10.4 update-service.md`

### Name
Update a service

### HTTP Method
`PUT`

### URL Path
`https://{workspaceUrl}/api/services/{service}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| service | integer or allOf | **required** | Service ID | `1` |

### Request Body Schema
Same as Create (10.2), but `name`, `recurring`, and `currency` are still required.

### Response Status Codes
| Code | Description |
|------|-------------|
| 201 | Success (Note: docs say 201, likely should be 200) |
| 400 | Bad Request - Validation error |
| 401 | Unauthorized |
| 404 | Not Found |

### Response Body Schema
Returns updated `Service` object (see 10.1 for schema)

### Notes / Gotchas
- Partial updates supported - unprovided fields remain unchanged
- Response code is 201 per documentation (unusual for update)

---

## 10.5 Delete a Service

### File Path
`spp-api-documentation/10. Services/10.5 delete-service.md`

### Name
Delete a service

### HTTP Method
`DELETE`

### URL Path
`https://{workspaceUrl}/api/services/{service}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| service | integer or allOf | **required** | Service ID | `1` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 204 | No Content - Deleted |
| 401 | Unauthorized |
| 404 | Not Found |

### Response Body Schema
No body (204)

### Example Request
```bash
curl --request DELETE \
  --url https://example.spp.co/api/services/1 \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123'
```

### Side Effects / State Changes
- **Soft delete** - can be undone
- Sets `deleted_at` timestamp

### Notes / Gotchas
- Soft delete - deletion can be undone
- Existing orders referencing the service are unaffected

---

## Pricing Configuration

### One-Time Services (`recurring: 0`)
- Uses `price` field directly

### Recurring Services (`recurring: 1`)
- `f_price` - First payment amount
- `f_period_l` - First period length
- `f_period_t` - First period type (D/W/M/Y)
- `r_price` - Recurring payment amount
- `r_period_l` - Recurring period length
- `r_period_t` - Recurring period type (D/W/M/Y)

### Trial/Setup Fee Services (`recurring: 2`)
- Initial fee with subsequent recurring

---

## Ambiguities and Missing Information

1. **Period Type Values:** D, W, M, Y assumed but not explicitly documented
2. **recurring_action Values:** Integer values not mapped to actions
3. **multi_order/request_orders:** Integer vs boolean inconsistency
4. **option_categories/option_variants:** How to configure options not documented
5. **HOTH Integration:** Purpose of hoth_product_key/hoth_package_name unclear
6. **provider_id/provider_service_id:** External provider integration not documented
7. **media Array:** Structure of media objects not documented
8. **clear_variants:** What exactly gets cleared not documented

---

## Cross-references

- Orders (7. Orders) - Orders reference services via `service_id`
- Subscriptions (11. Subscriptions) - Recurring services create subscriptions
- Team (13. Team) - `employees` references team members
