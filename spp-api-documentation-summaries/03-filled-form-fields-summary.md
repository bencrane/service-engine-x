# 3. FilledFormFields - API Documentation Summary

## Overview
The FilledFormFields API provides CRUD operations for managing form field data associated with orders or tickets. These are the actual values submitted by users through forms.

---

## 3.1 List All Filled Form Fields

### File Path
`spp-api-documentation/3. FilledFormFields/3.1 list-filled-form-fields.md`

### Name
List all filled form fields

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/form_data`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Request Headers
| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| Authorization | string | required | Bearer token | `Bearer 123` |
| X-Api-Version | string | optional | API version identifier | `2024-03-05` |

### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| order | any | conditional | Order ID - return fields for this order. Cannot be used with `ticket` |
| ticket | any | conditional | Ticket ID - return fields for this ticket. Cannot be used with `order` |

**Note:** Either `order` or `ticket` parameter must be provided, but not both.

### Path Parameters
None

### Request Body Schema
Not applicable (GET request)

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - missing or conflicting parameters |
| 401 | Unauthorized |

### Response Body Schema (200)
```json
{
  "data": [FilledFormField],
  "links": PaginationLinks,
  "meta": PaginationMeta
}
```

#### FilledFormField Object
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| id | integer | required | FilledFormField ID | `1` |
| created_at | string\<date-time\> | required | Created timestamp | `2021-08-26T14:55:23.000000Z` |
| updated_at | string\<date-time\> | required | Updated timestamp | `2021-08-26T14:55:23.000000Z` |
| submitted_at | string\<date-time\> | required | Submitted timestamp | `2021-08-26T14:55:23.000000Z` |
| form_field_id | integer | required | Form Field ID | `1` |
| field_id | integer | required | Field ID | `1` |
| formable_id | integer | required | Formable ID | `1` |
| formable_type | string | required | Formable type | `onboarding_form` |
| name | string | required | Field name | `Name` |
| type | string | required | Field type | `text` |
| value | string | required | Field value | `John Doe` |
| onboarding_field_id | integer | required | Onboarding field ID | `1` |
| onboarding_form_id | integer | required | Onboarding form ID | `1` |
| order_id | integer | required | Associated order ID | `1` |
| ticket_id | integer | required | Associated ticket ID | `1` |

### Example Request
```bash
curl --request GET \
  --url 'https://example.spp.co/api/form_data?order=123' \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'X-Api-Version: 2024-03-05'
```

### Example Response
```json
{
  "data": [
    {
      "created_at": "2021-08-26T14:55:23.000000Z",
      "form_field_id": 1,
      "field_id": 1,
      "formable_id": 1,
      "formable_type": "onboarding_form",
      "id": 1,
      "name": "Name",
      "onboarding_field_id": 1,
      "onboarding_form_id": 1,
      "order_id": 1,
      "submitted_at": "2021-08-26T14:55:23.000000Z",
      "ticket_id": 1,
      "type": "text",
      "updated_at": "2021-08-26T14:55:23.000000Z",
      "value": "John Doe"
    }
  ],
  "links": {...},
  "meta": {...}
}
```

### Side Effects / State Changes
None (read-only)

### Preconditions / Invariants
- Must provide either `order` or `ticket` parameter (not both)

### Error Cases
| Code | Error | Description |
|------|-------|-------------|
| 400 | Bad Request | Missing or conflicting order/ticket parameters |
| 401 | Unauthorized | Invalid or missing bearer token |

### Notes / Gotchas
- `order` and `ticket` are mutually exclusive parameters
- Type is `any` for order/ticket params (could be ID or string identifier)

### Cross-references
- Orders (7. Orders)
- Tickets (14. Tickets)

---

## 3.2 Create a Filled Form Field

### File Path
`spp-api-documentation/3. FilledFormFields/3.2 create-filled-form-field.md`

### Name
Create a filled form field

### HTTP Method
`POST`

### URL Path
`https://{workspaceUrl}/api/form_data`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Request Headers
| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| Authorization | string | required | Bearer token | `Bearer 123` |
| X-Api-Version | string | optional | API version identifier | `2024-03-05` |
| Content-Type | string | required | Request format | `application/json` |

### Path Parameters
None

### Query Parameters
None

### Request Body Schema
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| order | string | conditional | Order number. Cannot be used with `ticket` | `"E4A269FC"` |
| ticket | string | conditional | Ticket number. Cannot be used with `order` | `"T12345"` |
| name | string | **required** | Form field name | `"Do you accept ToS?"` |
| type | string | **required** | Form field type | `"text"` |
| value | string | **required** | Form field value | `"Yes"` |

**Allowed values for `type`:** `text`, `textarea`, `checkbox`, `data-dropdown`, `data-spreadsheet`, `file`

### Response Status Codes
| Code | Description |
|------|-------------|
| 201 | Created |
| 400 | Bad Request - validation error |
| 401 | Unauthorized |

### Response Body Schema (201)
Returns `FilledFormField` object (see 3.1 for schema)

### Example Request
```bash
curl --request POST \
  --url https://example.spp.co/api/form_data \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'Content-Type: application/json' \
  --data '{
  "order": "E4A269FC",
  "name": "Do you accept ToS?",
  "type": "text",
  "value": "Yes"
}'
```

### Example Response
```json
{
  "created_at": "2021-08-26T14:55:23.000000Z",
  "form_field_id": 1,
  "field_id": 1,
  "formable_id": 1,
  "formable_type": "onboarding_form",
  "id": 1,
  "name": "Do you accept ToS?",
  "onboarding_field_id": 1,
  "onboarding_form_id": 1,
  "order_id": 1,
  "submitted_at": "2021-08-26T14:55:23.000000Z",
  "ticket_id": 1,
  "type": "text",
  "updated_at": "2021-08-26T14:55:23.000000Z",
  "value": "Yes"
}
```

### Side Effects / State Changes
- Creates new form field data record
- Associates with specified order or ticket

### Preconditions / Invariants
- Either `order` or `ticket` must be provided (not both)
- Order/ticket must exist

### Error Cases
| Code | Error | Description |
|------|-------|-------------|
| 400 | Bad Request | Validation error or missing required fields |
| 401 | Unauthorized | Invalid or missing bearer token |

### Notes / Gotchas
- Documentation marks order/ticket as "REQUIRED" but not "required" in schema - clarification needed
- `order` and `ticket` use order/ticket number (string), not ID

### Cross-references
- Orders (7. Orders)
- Tickets (14. Tickets)

---

## 3.3 Retrieve a Filled Form Field

### File Path
`spp-api-documentation/3. FilledFormFields/3.3 retrieve-filled-form-field.md`

### Name
Retrieve a filled form field

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/form_data/{field}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| field | integer | **required** | Filled form field ID | `12` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |

### Response Body Schema (200)
Returns `FilledFormField` object (see 3.1 for schema)

### Example Request
```bash
curl --request GET \
  --url https://example.spp.co/api/form_data/12 \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123'
```

### Example Response
See 3.1 Example Response (single object, not array)

### Side Effects / State Changes
None (read-only)

### Error Cases
| Code | Error | Description |
|------|-------|-------------|
| 401 | Unauthorized | Invalid or missing bearer token |
| 404 | Not Found | Field ID doesn't exist |

---

## 3.4 Update a Filled Form Field

### File Path
`spp-api-documentation/3. FilledFormFields/3.4 update-filled-form-field.md`

### Name
Update a filled form field

### HTTP Method
`PUT`

### URL Path
`https://{workspaceUrl}/api/form_data/{field}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| field | integer | **required** | Filled form field ID | `12` |

### Request Body Schema
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| value | string | **required** | New field value | `"Yes"` |

**Note:** Only `value` can be updated. Name and type cannot be changed.

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |

### Response Body Schema (200)
Returns `FilledFormField` object (see 3.1 for schema)

### Example Request
```bash
curl --request PUT \
  --url https://example.spp.co/api/form_data/12 \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'Content-Type: application/json' \
  --data '{"value": "Updated Value"}'
```

### Side Effects / State Changes
- Updates field value
- Updates `updated_at` timestamp

### Error Cases
| Code | Error | Description |
|------|-------|-------------|
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Invalid or missing bearer token |
| 404 | Not Found | Field ID doesn't exist |

### Notes / Gotchas
- Only `value` field can be updated - `name` and `type` are immutable

---

## 3.5 Delete a Filled Form Field

### File Path
`spp-api-documentation/3. FilledFormFields/3.5 delete-filled-form-field.md`

### Name
Delete a filled form field

### HTTP Method
`DELETE`

### URL Path
`https://{workspaceUrl}/api/form_data/{field}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| field | integer | **required** | Filled form field ID | `12` |

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
  --url https://example.spp.co/api/form_data/12 \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123'
```

### Side Effects / State Changes
- **PERMANENT** deletion - cannot be undone

### Error Cases
| Code | Error | Description |
|------|-------|-------------|
| 401 | Unauthorized | Invalid or missing bearer token |
| 404 | Not Found | Field ID doesn't exist |

### Notes / Gotchas
- **WARNING:** Documentation explicitly states "It cannot be undone" - this is a hard delete, not soft delete

---

## Ambiguities and Missing Information

1. **Field Type Values:** Allowed types listed for create but not explained (what is `data-dropdown`, `data-spreadsheet`?)
2. **formable_type Values:** Only `onboarding_form` shown - what other values exist?
3. **Relationship Fields:** Multiple ID fields (form_field_id, field_id, onboarding_field_id) - unclear relationships
4. **Order/Ticket Parameter Types:** Listed as `any` in list endpoint but `string` in create endpoint
5. **Pagination on Retrieve:** Pagination links mentioned on retrieve endpoint (documentation error)
