# 2. Coupons - API Documentation Summary

## Overview
The Coupons API provides full CRUD operations for managing discount coupons. Coupons can be applied to services with various discount types, usage limits, and expiration dates.

---

## 2.1 List All Coupons

### File Path
`spp-api-documentation/2. Coupons/2.1 list-coupons.md`

### Name
List all coupons

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/coupons`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Request Headers
| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| Authorization | string | required | Bearer token | `Bearer 123` |
| X-Api-Version | string | optional | API version identifier | `2024-03-05` |
| Accept | string | required | Response format | `application/json` |

### Query Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| limit | integer | optional | Items per page | `10` |
| page | integer | optional | Page number | `1` |
| sort | string | optional | Sort by fields | `id:desc` |
| filters[id][$in][] | array[integer] | optional | Filter by IDs. Supports operators: $eq, $lt, $gt, $in | |

### Path Parameters
None

### Request Body Schema
Not applicable (GET request)

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success - Returns list of coupons |
| 401 | Unauthorized |

### Response Headers
| Header | Type | Description | Example |
|--------|------|-------------|---------|
| X-Api-Identifier | string | Unique request identifier | `efc995d2-bfdb-3bc9-80a3-e828bb9c83c2` |
| X-Api-Version | string | API version | `20231214` |

### Response Body Schema (200)
```json
{
  "data": [Coupon],
  "links": PaginationLinks,
  "meta": PaginationMeta
}
```

#### Coupon Object
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| id | integer | required | Coupon ID | `1` |
| code | string | required | Coupon code | `CODE` |
| type | string | required | Discount type | `percentage` |
| description | string | required | Description | `Description` |
| discounts | object | required | Discount configuration | `[{"amount":10,"services":[1]}]` |
| date_expires | string\<date-time\> | required | Expiration date | `2022-01-01 00:00:00` |
| new_customers | boolean | required | New customers only | `true` |
| single_use | boolean | required | Single use per customer | `true` |
| single_quantity | boolean | required | Single quantity | `true` |
| duration | boolean | required | Duration flag | `true` |
| min_cart_amount | number | required | Minimum cart amount | `1` |
| used_count | integer | required | Times used | `1` |
| affiliate | object or null | required | Affiliate info | `{}` |
| created_at | string\<date-time\> | required | Created timestamp | `2022-01-01T00:00:00Z` |
| updated_at | string\<date-time\> | required | Updated timestamp | `2022-01-01T00:00:00Z` |

#### PaginationLinks Object
| Field | Type | Description |
|-------|------|-------------|
| first | string | First page URL |
| last | string | Last page URL |
| prev | string or null | Previous page URL |
| next | string or null | Next page URL |

#### PaginationMeta Object
| Field | Type | Description |
|-------|------|-------------|
| current_page | integer | Current page number |
| from | integer | Starting record |
| last_page | integer | Last page number |
| links | array[object] | Page links array |
| path | string | Base path |
| per_page | integer | Items per page |
| to | integer | Ending record |
| total | integer | Total records |

### Example Request
```bash
curl --request GET \
  --url https://example.spp.co/api/coupons \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'X-Api-Version: '
```

### Example Response
```json
{
  "data": [
    {
      "id": 1,
      "code": "CODE",
      "type": "percentage",
      "description": "Description",
      "discounts": [{"amount": 10, "services": [1]}],
      "date_expires": "2022-01-01 00:00:00",
      "new_customers": true,
      "single_use": true,
      "single_quantity": true,
      "duration": true,
      "min_cart_amount": 1,
      "used_count": 1,
      "affiliate": {},
      "created_at": "2022-01-01T00:00:00Z",
      "updated_at": "2022-01-01T00:00:00Z"
    }
  ],
  "links": {
    "first": "https://example.spp.co/api/{resource}?page=1",
    "last": "https://example.spp.co/api/{resource}?page=3",
    "prev": null,
    "next": "https://example.spp.co/api/{resource}?page=2"
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 3,
    "per_page": 20,
    "to": 20,
    "total": 43
  }
}
```

### Side Effects / State Changes
None (read-only)

### Preconditions / Invariants
- Valid authentication token required

### Error Cases
| Code | Error | Description |
|------|-------|-------------|
| 401 | Unauthorized | Invalid or missing bearer token |

### Notes / Gotchas
- Results sorted by creation date (most recent first)
- Default pagination applies if limit/page not specified

### Cross-references
- Services (10. Services) - coupons reference service IDs in discounts

---

## 2.2 Create a Coupon

### File Path
`spp-api-documentation/2. Coupons/2.2 create-coupon.md`

### Name
Create a coupon

### HTTP Method
`POST`

### URL Path
`https://{workspaceUrl}/api/coupons`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Request Headers
| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| Authorization | string | required | Bearer token | `Bearer 123` |
| X-Api-Version | string | optional | API version identifier | `2024-03-05` |
| Accept | string | required | Response format | `application/json` |
| Content-Type | string | required | Request format | `application/json` |

### Path Parameters
None

### Query Parameters
None

### Request Body Schema
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| code | string | **required** | Coupon code | `CODE` |
| type | string | **required** | Discount type | `percentage` |
| description | string | optional | Description | `Description` |
| discounts | object | optional | Discount configuration | `[{"amount":10,"services":[1]}]` |
| usage_limit | integer | optional | Maximum uses | `1` |
| has_min_cart_amount | boolean | optional | Enable minimum cart | `true` |
| min_cart_amount | number | optional | Minimum cart value | `1` |
| date_expires | string\<date-time\> | optional | Expiration date | `2022-01-01 00:00:00` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 201 | Created - Coupon successfully created |
| 400 | Bad Request - Validation error |
| 401 | Unauthorized |

### Response Body Schema (201)
Returns `CouponResource` (see 2.1 for schema)

### Example Request
```bash
curl --request POST \
  --url https://example.spp.co/api/coupons \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'Content-Type: application/json' \
  --header 'X-Api-Version: ' \
  --data '{
  "code": "CODE",
  "description": "Description",
  "type": "percentage",
  "discounts": [{"amount": 10, "services": [1]}],
  "usage_limit": 1,
  "has_min_cart_amount": true,
  "min_cart_amount": 1,
  "date_expires": "2022-01-01 00:00:00"
}'
```

### Example Response
```json
{
  "id": 1,
  "code": "CODE",
  "type": "percentage",
  "description": "Description",
  "discounts": [{"amount": 10, "services": [1]}],
  "date_expires": "2022-01-01 00:00:00",
  "new_customers": true,
  "single_use": true,
  "single_quantity": true,
  "duration": true,
  "min_cart_amount": 1,
  "used_count": 1,
  "affiliate": {},
  "created_at": "2022-01-01T00:00:00Z",
  "updated_at": "2022-01-01T00:00:00Z"
}
```

### Side Effects / State Changes
- Creates new coupon record in database
- Coupon becomes immediately usable

### Preconditions / Invariants
- Valid authentication token required
- `code` must be unique (not documented but implied)

### Error Cases
| Code | Error | Description |
|------|-------|-------------|
| 400 | Bad Request | Validation failed (missing required fields) |
| 401 | Unauthorized | Invalid or missing bearer token |

### Notes / Gotchas
- **AMBIGUITY:** Request body has `usage_limit` but response has `single_use` - unclear relationship
- **AMBIGUITY:** Request body has `has_min_cart_amount` but response only has `min_cart_amount`
- Discounts object structure: `[{"amount": number, "services": [service_ids]}]`

### Cross-references
- Services (10. Services) - service IDs referenced in discounts array

---

## 2.3 Retrieve a Coupon

### File Path
`spp-api-documentation/2. Coupons/2.3 retrieve-coupon.md`

### Name
Retrieve a coupon

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/coupons/{coupon}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Request Headers
| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| Authorization | string | required | Bearer token | `Bearer 123` |
| X-Api-Version | string | optional | API version identifier | `2024-03-05` |
| Accept | string | required | Response format | `application/json` |

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| coupon | integer or allOf | **required** | Coupon ID | `1` |

### Query Parameters
None

### Request Body Schema
Not applicable (GET request)

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success - Returns coupon |
| 401 | Unauthorized |
| 404 | Not Found - Coupon doesn't exist |

### Response Body Schema (200)
Returns `CouponResource` (see 2.1 for schema)

### Example Request
```bash
curl --request GET \
  --url https://example.spp.co/api/coupons/{coupon} \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'X-Api-Version: '
```

### Example Response
```json
{
  "id": 1,
  "code": "CODE",
  "type": "percentage",
  "description": "Description",
  "discounts": [{"amount": 10, "services": [1]}],
  "date_expires": "2022-01-01 00:00:00",
  "new_customers": true,
  "single_use": true,
  "single_quantity": true,
  "duration": true,
  "min_cart_amount": 1,
  "used_count": 1,
  "affiliate": {},
  "created_at": "2022-01-01T00:00:00Z",
  "updated_at": "2022-01-01T00:00:00Z"
}
```

### Side Effects / State Changes
None (read-only)

### Preconditions / Invariants
- Coupon with given ID must exist

### Error Cases
| Code | Error | Description |
|------|-------|-------------|
| 401 | Unauthorized | Invalid or missing bearer token |
| 404 | Not Found | Coupon ID doesn't exist |

### Notes / Gotchas
- **AMBIGUITY:** Path parameter type "integer or allOf" is unclear

### Cross-references
None

---

## 2.4 Update a Coupon

### File Path
`spp-api-documentation/2. Coupons/2.4 update-coupon.md`

### Name
Update a coupon

### HTTP Method
`PUT`

### URL Path
`https://{workspaceUrl}/api/coupons/{coupon}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Request Headers
| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| Authorization | string | required | Bearer token | `Bearer 123` |
| X-Api-Version | string | optional | API version identifier | `2024-03-05` |
| Accept | string | required | Response format | `application/json` |
| Content-Type | string | required | Request format | `application/json` |

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| coupon | integer or allOf | **required** | Coupon ID | `1` |

### Query Parameters
None

### Request Body Schema
Same as Create (2.2) - partial updates supported (parameters not provided are left unchanged)

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| code | string | **required** | Coupon code | `CODE` |
| type | string | **required** | Discount type | `percentage` |
| description | string | optional | Description | `Description` |
| discounts | object | optional | Discount configuration | `[{"amount":10,"services":[1]}]` |
| usage_limit | integer | optional | Maximum uses | `1` |
| has_min_cart_amount | boolean | optional | Enable minimum cart | `true` |
| min_cart_amount | number | optional | Minimum cart value | `1` |
| date_expires | string\<date-time\> | optional | Expiration date | `2022-01-01 00:00:00` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 201 | Success - Coupon updated |
| 400 | Bad Request - Validation error |
| 401 | Unauthorized |
| 404 | Not Found - Coupon doesn't exist |

### Response Body Schema (201)
Returns `CouponResource` (see 2.1 for schema)

### Example Request
```bash
curl --request PUT \
  --url https://example.spp.co/api/coupons/{coupon} \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'Content-Type: application/json' \
  --header 'X-Api-Version: ' \
  --data '{
  "code": "CODE",
  "description": "Updated Description",
  "type": "percentage"
}'
```

### Example Response
See 2.2 Example Response

### Side Effects / State Changes
- Updates coupon record
- `updated_at` timestamp changes

### Preconditions / Invariants
- Coupon must exist

### Error Cases
| Code | Error | Description |
|------|-------|-------------|
| 400 | Bad Request | Validation failed |
| 401 | Unauthorized | Invalid or missing bearer token |
| 404 | Not Found | Coupon ID doesn't exist |

### Notes / Gotchas
- **ANOMALY:** Returns 201 instead of typical 200 for updates
- Documentation states "accepts mostly the same arguments as creation" - implies some differences not specified
- `code` and `type` are still required even for partial updates

### Cross-references
- 2.2 Create a Coupon - same request body schema

---

## 2.5 Delete a Coupon

### File Path
`spp-api-documentation/2. Coupons/2.5 delete-coupon.md`

### Name
Delete a coupon

### HTTP Method
`DELETE`

### URL Path
`https://{workspaceUrl}/api/coupons/{coupon}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Request Headers
| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| Authorization | string | required | Bearer token | `Bearer 123` |
| X-Api-Version | string | optional | API version identifier | `2024-03-05` |
| Accept | string | required | Response format | `application/json` |

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| coupon | integer or allOf | **required** | Coupon ID | `1` |

### Query Parameters
None

### Request Body Schema
Not applicable (DELETE request)

### Response Status Codes
| Code | Description |
|------|-------------|
| 204 | No Content - Coupon deleted |
| 401 | Unauthorized |
| 404 | Not Found - Coupon doesn't exist |

### Response Body Schema
No body returned (204)

### Example Request
```bash
curl --request DELETE \
  --url https://example.spp.co/api/coupons/{coupon} \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'X-Api-Version: '
```

### Example Response
No body (204 No Content)

### Side Effects / State Changes
- Soft deletes coupon (can be undone per documentation)
- Coupon no longer usable

### Preconditions / Invariants
- Coupon must exist

### Error Cases
| Code | Error | Description |
|------|-------|-------------|
| 401 | Unauthorized | Invalid or missing bearer token |
| 404 | Not Found | Coupon ID doesn't exist |

### Notes / Gotchas
- **IMPORTANT:** Documentation states "It can be undone" - implies soft delete
- No endpoint documented for restoring deleted coupons

### Cross-references
None

---

## Ambiguities and Missing Information

1. **Discount Types:** Documentation shows `percentage` but doesn't list all valid `type` values (e.g., `fixed`, `amount`?)
2. **Discounts Object Structure:** The `discounts` field is typed as `object` but examples show an array of objects
3. **Request vs Response Field Mismatch:** Request has `usage_limit`, `has_min_cart_amount` but response has `single_use`, `single_quantity`, `duration` - relationship unclear
4. **allOf Type:** Path parameters use "integer or allOf" which is ambiguous
5. **Affiliate Object:** Structure not documented
6. **Coupon Restoration:** Soft delete mentioned but no restore endpoint documented
7. **Update Returns 201:** Unusual - typically updates return 200
8. **Pagination on Single Resource:** Pagination links mentioned on retrieve/update/delete endpoints (seems like documentation error)
