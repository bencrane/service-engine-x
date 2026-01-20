# 4. Invoices - API Documentation Summary

## Overview
The Invoices API provides CRUD operations plus specialized endpoints for charging invoices and marking them as paid. Invoices are linked to clients, orders, and services.

---

## 4.1 Charge an Invoice

### File Path
`spp-api-documentation/4. Invoices/4.1 charge-invoice.md`

### Name
Charge an invoice

### HTTP Method
`POST`

### URL Path
`https://{workspaceUrl}/api/invoices/{invoice}/charge`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| invoice | string or allOf | **required** | Invoice ID/number | `E4A269FC` |

### Request Body Schema
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| payment_method_id | string | **required** | Stripe payment method ID | `pm_1J5gXt2eZvKYlo2C3X2Z2Z2Z` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success - Invoice charged |
| 400 | Bad Request |
| 401 | Unauthorized |

### Response Body Schema (200)
Returns full `Invoice` object (see 4.2 for schema)

### Side Effects / State Changes
- Charges the invoice using the provided payment method
- Removes custom billing date if set
- Updates invoice status
- Creates transaction record

### Notes / Gotchas
- **IMPORTANT:** Uses Stripe payment method IDs (format: `pm_xxx`)
- Custom billing date is removed upon charging

---

## 4.2 List All Invoices

### File Path
`spp-api-documentation/4. Invoices/4.2 list-invoices.md`

### Name
List all invoices

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/invoices`

### Query Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| limit | integer | optional | Items per page | `10` |
| page | integer | optional | Page number | `1` |
| sort | string | optional | Sort by fields | `id:desc` |
| filters[user_id][$in][] | array[integer] | optional | Filter by user IDs | |
| filters[status][$eq] | string | optional | Filter by status | |

### Response Body Schema (200)
```json
{
  "data": [Invoice],
  "links": PaginationLinks,
  "meta": PaginationMeta
}
```

#### Invoice Object
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| id | integer | required | Invoice ID | `1` |
| number | string | required | Invoice number | `E4A269FC` |
| number_prefix | string | optional | Number prefix | `SPP-` |
| client | User | required | Client object | |
| items | array[InvoiceItem] | required | Line items | |
| billing_address | Address | required | Billing address | |
| status | string | required | Status text | `Unpaid` |
| status_id | integer | required | Status ID | `1` |
| created_at | string\<date-time\> | required | Created date | `2021-01-01T00:00:00+00:00` |
| date_due | string\<date-time\> | required | Due date | `2021-01-01T00:00:00+00` |
| date_paid | string\<date-time\> | required | Paid date | `2021-01-01T00:00:00+00:00` |
| credit | number | required | Credit applied | `10.00` |
| tax | number | required | Tax amount | `10.00` |
| tax_name | string | required | Tax name | `Tax` |
| tax_percent | number | required | Tax percentage | `10.00` |
| currency | string | required | Currency code | `USD` |
| reason | string | required | Invoice reason | `Reason` |
| note | string | required | Note | `Note` |
| ip_address | string | required | Client IP | `127.0.0.1` |
| loc_confirm | boolean | required | Location confirmed | `false` |
| recurring | object | required | Recurring config | `{"r_period_l":12,"r_period_t":"M"}` |
| coupon_id | integer | required | Applied coupon ID | `1` |
| transaction_id | string | required | Transaction ID | `123456789` |
| paysys | string | required | Payment system | `Stripe` |
| subtotal | number | required | Subtotal | `10.00` |
| total | number | required | Total | `10.00` |
| employee_id | integer | required | Employee ID | `1` |
| view_link | string | required | View link with key | |
| download_link | string | required | Download link with key | |
| thanks_link | string | required | Thanks page link | |

#### InvoiceItem Object
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| id | integer | required | Item ID | `1` |
| invoice_id | integer | required | Parent invoice ID | `1` |
| name | string | required | Item name | `Name` |
| description | string | required | Description | `Description` |
| amount | string | required | Unit amount | `10.00` |
| quantity | integer | required | Quantity | `1` |
| discount | string | required | Discount | `0.00` |
| discount2 | string | required | Secondary discount | `0.00` |
| total | string | required | Line total | `10.00` |
| options | object | required | Selected options | `{"Size":"S","Color":"Yellow"}` |
| order_id | integer | required | Associated order ID | `1` |
| service_id | integer | required | Service ID | `1` |
| created_at | string\<date-time\> | required | Created date | |
| updated_at | string\<date-time\> | required | Updated date | |

---

## 4.3 Create an Invoice

### File Path
`spp-api-documentation/4. Invoices/4.3 create-invoice.md`

### Name
Create an invoice

### HTTP Method
`POST`

### URL Path
`https://{workspaceUrl}/api/invoices`

### Request Body Schema
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | integer | **required** | Client user ID |
| items | array[object] | **required** | Line items |
| items[].name | string | **required** | Item name |
| items[].amount | number | **required** | Item amount |
| items[].quantity | integer | optional | Quantity (default 1) |
| date_due | string\<date-time\> | optional | Due date |
| note | string | optional | Invoice note |
| coupon_id | integer | optional | Coupon to apply |

### Response Status Codes
| Code | Description |
|------|-------------|
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |

---

## 4.4 Retrieve an Invoice

### File Path
`spp-api-documentation/4. Invoices/4.4 retrieve-invoice.md`

### Name
Retrieve an invoice

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/invoices/{invoice}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| invoice | string or allOf | **required** | Invoice ID/number | `E4A269FC` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |

---

## 4.5 Update an Invoice

### File Path
`spp-api-documentation/4. Invoices/4.5 update-invoice.md`

### Name
Update an invoice

### HTTP Method
`PUT`

### URL Path
`https://{workspaceUrl}/api/invoices/{invoice}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| invoice | string or allOf | **required** | Invoice ID/number | `E4A269FC` |

### Request Body Schema
Partial update supported - only provided fields are changed.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| date_due | string\<date-time\> | optional | Due date |
| note | string | optional | Invoice note |
| status | integer | optional | Status ID |

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |

---

## 4.6 Delete an Invoice

### File Path
`spp-api-documentation/4. Invoices/4.6 delete-invoice.md`

### Name
Delete an invoice

### HTTP Method
`DELETE`

### URL Path
`https://{workspaceUrl}/api/invoices/{invoice}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| invoice | string or allOf | **required** | Invoice ID/number | `E4A269FC` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 204 | No Content - Deleted |
| 401 | Unauthorized |
| 404 | Not Found |

### Notes / Gotchas
- Deletion is soft delete (can be undone per documentation pattern)

---

## 4.7 Mark Invoice as Paid

### File Path
`spp-api-documentation/4. Invoices/4.7 mark-invoice-paid.md`

### Name
Mark invoice as paid

### HTTP Method
`POST`

### URL Path
`https://{workspaceUrl}/api/invoices/{invoice}/paid`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| invoice | string or allOf | **required** | Invoice ID/number | `E4A269FC` |

### Request Body Schema
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| paysys | string | optional | Payment system used | `Cash` |
| transaction_id | string | optional | External transaction ID | `manual-001` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |

### Side Effects / State Changes
- Updates invoice status to "Paid"
- Sets `date_paid` to current timestamp
- Records payment system and transaction ID
- May trigger order status changes

### Notes / Gotchas
- Use this for manual/offline payments
- Different from 4.1 Charge which processes payment via Stripe

---

## Ambiguities and Missing Information

1. **Status Values:** Full list of `status`/`status_id` values not documented
2. **recurring Object:** Structure `{"r_period_l":12,"r_period_t":"M"}` - meanings not explained (likely: r_period_l = length, r_period_t = type M=Month?)
3. **paysys Values:** List of valid payment system identifiers not provided
4. **Invoice vs Order:** Relationship between invoices and orders not fully documented
5. **loc_confirm:** Purpose unclear ("location confirm"?)
6. **Credit Application:** How credits are applied not documented
7. **discount vs discount2:** Purpose of two discount fields not explained
