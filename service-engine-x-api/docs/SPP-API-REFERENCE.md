# SPP.co API Reference

**Version:** 2024-03-05
**Base URL:** `https://{workspaceUrl}/api`

This document consolidates the SPP.co API conventions, patterns, and resources.

---

## Table of Contents

1. [Authentication](#authentication)
2. [Headers](#headers)
3. [Pagination](#pagination)
4. [Filtering & Sorting](#filtering--sorting)
5. [Response Structure](#response-structure)
6. [Status Codes](#status-codes)
7. [Resources](#resources)
8. [Common Data Types](#common-data-types)

---

## Authentication

All API requests require authentication via Bearer token.

```
Authorization: Bearer {api_token}
```

### Example Request

```bash
curl --request GET \
  --url https://example.spp.co/api/orders \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer your_api_token_here'
```

---

## Headers

### Request Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Authorization` | string | Yes | Bearer token for authentication |
| `Accept` | string | Yes | Should be `application/json` |
| `Content-Type` | string | For POST/PUT | Should be `application/json` |
| `X-Api-Version` | string | No | API version identifier (e.g., `2024-03-05`) |

### Response Headers

| Header | Type | Description |
|--------|------|-------------|
| `X-Api-Identifier` | string | Unique request identifier for support |
| `X-Api-Version` | string | API version used for the response |

---

## Pagination

All list endpoints return paginated responses.

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Items per page (max varies by endpoint) |
| `page` | integer | 1 | Page number |

### Response Structure

```json
{
  "data": [...],
  "links": {
    "first": "https://example.spp.co/api/{resource}?page=1",
    "last": "https://example.spp.co/api/{resource}?page=3",
    "prev": null,
    "next": "https://example.spp.co/api/{resource}?page=2"
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "to": 20,
    "last_page": 3,
    "per_page": 20,
    "total": 43,
    "path": "https://example.spp.co/api/{resource}",
    "links": [
      {"url": null, "label": "Previous", "active": false},
      {"url": "...?page=1", "label": "1", "active": true},
      {"url": "...?page=2", "label": "2", "active": false},
      {"url": "...?page=2", "label": "Next", "active": false}
    ]
  }
}
```

### Pagination Fields

| Field | Type | Description |
|-------|------|-------------|
| `current_page` | integer | Current page number |
| `from` | integer | First item index on current page |
| `to` | integer | Last item index on current page |
| `last_page` | integer | Total number of pages |
| `per_page` | integer | Items per page |
| `total` | integer | Total number of items |
| `path` | string | Base URL for the resource |

---

## Filtering & Sorting

### Sorting

Use the `sort` parameter with format `field:direction`.

```
?sort=created_at:desc
?sort=id:asc
?sort=name:asc
```

**Directions:** `asc`, `desc`

### Filtering

Use the `filters` parameter with format `filters[field][$operator]=value`.

#### Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `$eq` | Equals | `filters[status][$eq]=1` |
| `$lt` | Less than | `filters[created_at][$lt]=2024-01-01` |
| `$gt` | Greater than | `filters[price][$gt]=100` |
| `$in` | In array | `filters[user_id][$in][]=1&filters[user_id][$in][]=2` |

#### Filter Examples

```bash
# Filter by user ID
?filters[user_id][$eq]=123

# Filter by multiple IDs
?filters[id][$in][]=1&filters[id][$in][]=2&filters[id][$in][]=3

# Filter by date range
?filters[created_at][$gt]=2024-01-01&filters[created_at][$lt]=2024-12-31

# Combine multiple filters
?filters[status][$eq]=1&filters[user_id][$eq]=123&sort=created_at:desc
```

### Expanding Relations

Some endpoints support expanding related resources using `expand[]`.

```
?expand[]=client
?expand[]=invoice
?expand[]=client&expand[]=service
```

---

## Response Structure

### Success Response (Single Resource)

```json
{
  "id": 1,
  "name": "Resource Name",
  "created_at": "2021-09-01T00:00:00+00:00",
  "updated_at": "2021-09-01T00:00:00+00:00",
  ...
}
```

### Success Response (List)

```json
{
  "data": [
    {"id": 1, ...},
    {"id": 2, ...}
  ],
  "links": {...},
  "meta": {...}
}
```

### Error Response

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "field_name": ["Error message for this field."]
  }
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Created |
| `204` | No Content (successful delete) |
| `400` | Bad Request |
| `401` | Unauthorized |
| `404` | Not Found |
| `422` | Validation Error |
| `500` | Internal Server Error |

---

## Resources

### Overview

| Resource | Endpoint | Description |
|----------|----------|-------------|
| Clients | `/api/clients` | Customer accounts |
| Orders | `/api/orders` | Order transactions |
| Services | `/api/services` | Service catalog |
| Invoices | `/api/invoices` | Billing invoices |
| Tickets | `/api/tickets` | Support tickets |
| Subscriptions | `/api/subscriptions` | Recurring subscriptions |
| Coupons | `/api/coupons` | Discount coupons |
| Tags | `/api/tags` | Resource tags |
| Team | `/api/team` | Team members |

---

### Clients

Customer accounts in the system.

#### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/clients` | List all clients |
| `POST` | `/api/clients` | Create a client |
| `GET` | `/api/clients/{id}` | Retrieve a client |
| `PUT` | `/api/clients/{id}` | Update a client |
| `DELETE` | `/api/clients/{id}` | Delete a client |

#### Client Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Client ID |
| `name_f` | string | First name |
| `name_l` | string | Last name |
| `name` | string | Full name (computed) |
| `email` | string | Email address |
| `company` | string | Company name |
| `phone` | string | Phone number |
| `tax_id` | string | Tax ID |
| `address` | Address | Billing address |
| `note` | string | Internal notes |
| `balance` | number | Account balance |
| `spent` | string | Total spent |
| `optin` | string | Marketing opt-in status |
| `stripe_id` | string | Stripe customer ID |
| `custom_fields` | object | Custom field values |
| `status` | integer | Account status |
| `role_id` | integer | Role ID |
| `role` | Role | Role object |
| `aff_id` | integer | Affiliate ID |
| `aff_link` | string | Affiliate referral link |
| `created_at` | datetime | Date created |

#### Create Client Request

```json
{
  "name_f": "John",
  "name_l": "Doe",
  "email": "john@example.com",
  "company": "Acme Inc.",
  "phone": "555-123-4567",
  "address": {
    "line_1": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postcode": "10001",
    "country": "US"
  },
  "note": "VIP customer",
  "status_id": 1
}
```

---

### Orders

Order transactions and work tracking.

#### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/orders` | List all orders |
| `POST` | `/api/orders` | Create an order |
| `GET` | `/api/orders/{id}` | Retrieve an order |
| `PUT` | `/api/orders/{id}` | Update an order |
| `DELETE` | `/api/orders/{id}` | Delete an order |

#### Order Object (Index)

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Order ID |
| `user_id` | integer | Client user ID |
| `client` | User | Client object |
| `service_id` | integer | Service ID |
| `service` | string | Service name |
| `status` | string | Order status (label) |
| `price` | number | Order price |
| `quantity` | integer | Quantity |
| `currency` | string | Currency code |
| `invoice_id` | integer | Related invoice ID |
| `note` | string | Order notes |
| `form_data` | object | Form field values |
| `metadata` | object | Custom metadata |
| `tags` | array[string] | Tags |
| `employees` | array[object] | Assigned employees |
| `paysys` | string | Payment system used |
| `date_started` | datetime | Work start date |
| `date_completed` | datetime | Completion date |
| `date_due` | datetime | Due date |
| `last_message_at` | datetime | Last message timestamp |
| `created_at` | datetime | Date created |
| `updated_at` | datetime | Date updated |

#### Order Statuses

| Status | Description |
|--------|-------------|
| Unpaid | Awaiting payment |
| In Progress | Work ongoing |
| Completed | Work finished |
| Cancelled | Order cancelled |
| On Hold | Work paused |

#### Create Order Request

```json
{
  "user_id": 1,
  "service_id": 5,
  "service": "Custom Service Name",
  "status": 1,
  "note": "Order notes",
  "date_due": "2024-12-31T00:00:00+00:00",
  "employees": [2, 3],
  "tags": ["priority", "rush"],
  "metadata": {
    "custom_field": "value"
  }
}
```

---

### Services

Service catalog items.

#### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/services` | List all services |
| `POST` | `/api/services` | Create a service |
| `GET` | `/api/services/{id}` | Retrieve a service |
| `PUT` | `/api/services/{id}` | Update a service |
| `DELETE` | `/api/services/{id}` | Delete a service |

#### Service Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Service ID |
| `name` | string | Service name |
| `description` | string | Description |
| `image` | string | Image URL |
| `price` | number | Base price |
| `pretty_price` | string | Formatted price (e.g., "$100.00") |
| `currency` | string | Currency code |
| `recurring` | boolean | Is recurring subscription |
| `f_price` | number | First payment amount |
| `f_period_l` | integer | First period length |
| `f_period_t` | string | First period type (day, week, month) |
| `r_price` | number | Recurring payment amount |
| `r_period_l` | integer | Recurring period length |
| `r_period_t` | string | Recurring period type |
| `recurring_action` | string | Action when recurring ends |
| `multi_order` | boolean | Allow multiple orders |
| `request_orders` | boolean | Request-based orders |
| `deadline` | integer | Default deadline (days) |
| `public` | boolean | Publicly visible |
| `sort_order` | integer | Display order |
| `folder_id` | integer | Folder ID |
| `metadata` | object | Custom metadata |
| `created_at` | datetime | Date created |
| `updated_at` | datetime | Date updated |
| `deleted_at` | datetime | Soft delete timestamp |

---

### Invoices

Billing invoices.

#### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/invoices` | List all invoices |
| `POST` | `/api/invoices` | Create an invoice |
| `GET` | `/api/invoices/{id}` | Retrieve an invoice |
| `PUT` | `/api/invoices/{id}` | Update an invoice |
| `DELETE` | `/api/invoices/{id}` | Delete an invoice |
| `POST` | `/api/invoices/{id}/charge` | Charge an invoice |
| `POST` | `/api/invoices/{id}/mark-paid` | Mark invoice as paid |

#### Invoice Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Invoice ID |
| `number` | string | Invoice number |
| `number_prefix` | string | Number prefix (e.g., "SPP-") |
| `client` | User | Client object |
| `items` | array[InvoiceItem] | Line items |
| `billing_address` | Address | Billing address |
| `status` | string | Status label |
| `status_id` | integer | Status ID |
| `subtotal` | number | Subtotal |
| `tax` | number | Tax amount |
| `tax_name` | string | Tax name |
| `tax_percent` | number | Tax percentage |
| `total` | number | Total amount |
| `credit` | number | Credit applied |
| `currency` | string | Currency code |
| `coupon_id` | integer | Applied coupon ID |
| `paysys` | string | Payment system |
| `transaction_id` | string | Transaction ID |
| `note` | string | Invoice notes |
| `reason` | string | Invoice reason |
| `recurring` | object | Recurring details |
| `date_due` | datetime | Due date |
| `date_paid` | datetime | Payment date |
| `view_link` | string | Public view URL |
| `download_link` | string | PDF download URL |
| `thanks_link` | string | Thank you page URL |
| `created_at` | datetime | Date created |

#### Invoice Status IDs

| ID | Status |
|----|--------|
| 1 | Unpaid |
| 2 | Paid |
| 3 | Cancelled |
| 4 | Refunded |

---

### Tickets

Support tickets.

#### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/tickets` | List all tickets |
| `POST` | `/api/tickets` | Create a ticket |
| `GET` | `/api/tickets/{id}` | Retrieve a ticket |
| `PUT` | `/api/tickets/{id}` | Update a ticket |
| `DELETE` | `/api/tickets/{id}` | Delete a ticket |

#### Ticket Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Ticket ID |
| `subject` | string | Ticket subject |
| `user_id` | integer | Client user ID |
| `client` | User | Client object |
| `status` | string | Ticket status |
| `source` | string | Ticket source |
| `order_id` | integer | Related order ID |
| `form_data` | object | Form field values |
| `tags` | array[string] | Tags |
| `note` | string | Internal notes |
| `employees` | array[object] | Assigned employees |
| `messages` | array[Message] | Ticket messages |
| `metadata` | object | Custom metadata |
| `date_closed` | datetime | Close date |
| `last_message_at` | datetime | Last message timestamp |
| `created_at` | datetime | Date created |
| `updated_at` | datetime | Date updated |

---

### Order Messages

Messages within orders.

#### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/order-messages` | List all order messages |
| `POST` | `/api/order-messages` | Create a message |
| `DELETE` | `/api/order-messages/{id}` | Delete a message |

#### Message Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Message ID |
| `user_id` | integer | Sender user ID |
| `message` | string | Message content |
| `staff_only` | boolean | Internal message flag |
| `files` | array[string] | Attached file URLs |
| `created_at` | datetime | Date created |

---

### Order Tasks

Tasks within orders.

#### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/order-tasks` | List all tasks |
| `POST` | `/api/order-tasks` | Create a task |
| `PUT` | `/api/order-tasks/{id}` | Update a task |
| `DELETE` | `/api/order-tasks/{id}` | Delete a task |

#### Task Completion

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/order-tasks/{id}/complete` | Mark task complete |
| `POST` | `/api/order-tasks/{id}/incomplete` | Mark task incomplete |

---

### Subscriptions

Recurring subscriptions.

#### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/subscriptions` | List all subscriptions |
| `GET` | `/api/subscriptions/{id}` | Retrieve a subscription |
| `PUT` | `/api/subscriptions/{id}` | Update a subscription |

#### Subscription Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Subscription ID |
| `number` | string | Subscription number |
| `client` | User | Client object |
| `status` | string | Status |
| `processor_id` | string | Payment processor ID |
| `current_period_end` | datetime | Current period end date |
| `payments` | array[object] | Payment history |
| `orders` | array[string] | Related order IDs |
| `payment_count` | integer | Total payment count |

---

### Tags

Resource tags.

#### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/tags` | List all tags |

---

### Team

Team members (employees).

#### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/team` | List all team members |
| `GET` | `/api/team/{id}` | Retrieve a team member |

---

### Coupons

Discount coupons.

#### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/coupons` | List all coupons |
| `POST` | `/api/coupons` | Create a coupon |
| `GET` | `/api/coupons/{id}` | Retrieve a coupon |
| `PUT` | `/api/coupons/{id}` | Update a coupon |
| `DELETE` | `/api/coupons/{id}` | Delete a coupon |

---

### Magic Links

Passwordless authentication links.

#### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/magic-link` | Generate a magic link |

---

## Common Data Types

### Address

```json
{
  "line_1": "123 Main St",
  "line_2": "Suite 100",
  "city": "New York",
  "state": "NY",
  "postcode": "10001",
  "country": "US",
  "name_f": "John",
  "name_l": "Doe",
  "tax_id": "123456789",
  "company_name": "Acme Inc.",
  "company_vat": "123456789"
}
```

### Role

```json
{
  "id": 1,
  "name": "Administrator",
  "dashboard_access": 3,
  "clients": 3,
  "orders": 3,
  "services": 3,
  "invoices": 3,
  "tickets": 3,
  "team": true,
  "settings": 1,
  "created_at": "2021-08-31T14:48:00+00:00",
  "updated_at": "2021-08-31T14:48:00+00:00"
}
```

### Permission Levels

| Level | Meaning |
|-------|---------|
| 0 | No access |
| 1 | View only |
| 2 | View + Edit |
| 3 | Full access (View + Edit + Delete) |

### Invoice Item

```json
{
  "id": 1,
  "invoice_id": 1,
  "name": "Service Name",
  "description": "Item description",
  "amount": "100.00",
  "quantity": 1,
  "discount": "0.00",
  "total": "100.00",
  "service_id": 5,
  "order_id": 10,
  "options": {"Size": "Large"},
  "created_at": "2021-08-31T14:48:00+00:00",
  "updated_at": "2021-08-31T14:48:00+00:00"
}
```

### Employee (Assignee)

```json
{
  "id": 1,
  "name_f": "John",
  "name_l": "Doe",
  "group_id": 1,
  "role_id": 1
}
```

### User Manager

```json
{
  "id": 25,
  "name": "John Doe",
  "name_f": "John",
  "name_l": "Doe",
  "email": "manager@example.org",
  "role_id": 5
}
```

---

## Date/Time Format

All dates use ISO 8601 format with timezone:

```
2021-09-01T00:00:00+00:00
```

---

## ID Types

SPP uses **integer IDs** for all resources:

```json
{
  "id": 1,
  "user_id": 123,
  "service_id": 45
}
```

---

## Soft Deletes

Some resources support soft deletion. Soft-deleted records include a `deleted_at` timestamp and are excluded from list queries by default.

---

## Rate Limiting

The API has rate limits. If you exceed them, you'll receive a `429 Too Many Requests` response. Include appropriate delays between requests when processing bulk operations.

---

## Webhooks

SPP supports webhooks for real-time event notifications. Configure webhooks in your workspace settings to receive events like:

- Order created/updated
- Invoice paid
- Ticket created
- Client registered

---

## Support

For API issues, include these headers in your support request:

- `X-Api-Identifier` (from response)
- `X-Api-Version` (from response)
- Request timestamp
- Endpoint called
