# 17. Clients - API Documentation Summary

## Overview
The Clients API provides full CRUD operations for managing client (customer) users. Clients are users who can place orders, submit tickets, and interact with the service platform.

---

## 17.1 List All Clients

### File Path
`spp-api-documentation/17. Clients/17.1 list-clients.md`

### Name
List all clients

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/clients`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Query Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| limit | integer | optional | Items per page | `10` |
| page | integer | optional | Page number | `1` |
| sort | string | optional | Sort by fields | `id:desc` |
| filters[email][$eq] | string | optional | Filter by email | `user@example.org` |
| filters[status][$eq] | integer | optional | Filter by status | `1` |

**Supported Filter Operators:** `$eq` (=), `$lt` (<), `$gt` (>), `$in` (in array)

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

### Response Body Schema (200)
```json
{
  "data": [Client],
  "links": PaginationLinks,
  "meta": PaginationMeta
}
```

#### Client Object
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| id | integer | required | User ID | `1` |
| name | string | required | Full name | `John Doe` |
| name_f | string | required | First name | `John` |
| name_l | string | required | Last name | `Doe` |
| email | string | required | Email address | `user@example.org` |
| company | string | required | Company name | `Example Inc.` |
| tax_id | string | required | Tax ID | `123456789` |
| phone | string | required | Phone number | `123456789` |
| address | Address | required | Full address object | |
| note | string | required | Internal note | `Note` |
| balance | number | required | Account balance | `10.00` |
| spent | string | optional | Total spent | `10.00` |
| optin | string | required | Marketing consent | `Yes` |
| stripe_id | string | required | Stripe customer ID | `stripe_id` |
| custom_fields | object | required | Custom field data | `{}` |
| status | integer | required | Account status | `1` |
| role_id | integer | required | Role ID | `1` |
| role | Role | required | Full role object | |
| aff_id | integer | required | Affiliate ID | `1` |
| aff_link | string | required | Affiliate link | `https://example.spp.co/r/ABC123` |
| ga_cid | string | required | Google Analytics client ID | `123456789.1234567890` |
| employee_id | integer | required | Assigned employee ID | `2` |
| managers | array[UserManager] | required | Assigned managers | |
| team_owner_ids | array[integer] | required | Team owner IDs | `[6]` |
| team_member_ids | array[integer] | required | Team member IDs | `[9]` |
| created_at | string\<date-time\> | required | Created timestamp | |

#### Address Object
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| line_1 | string | required | Address line 1 | `123 Main St` |
| line_2 | string | required | Address line 2 | `Suite 100` |
| city | string | required | City | `New York` |
| state | string | required | State/Province | `NY` |
| country | string | required | Country code | `US` |
| postcode | string | required | Postal code | `10001` |
| name_f | string | required | First name | `John` |
| name_l | string | required | Last name | `Doe` |
| tax_id | string | required | Tax ID | `123456789` |
| company_name | string | required | Company name | `Acme Inc.` |
| company_vat | string | required | Company VAT | `123456789` |

---

## 17.2 Create a Client

### File Path
`spp-api-documentation/17. Clients/17.2 create-client.md`

### Name
Create a client

### HTTP Method
`POST`

### URL Path
`https://{workspaceUrl}/api/clients`

### Request Body Schema
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| email | string | **required** | Email address | `user@example.org` |
| name_f | string | **required** | First name | `John` |
| name_l | string | **required** | Last name | `Doe` |
| company | string | optional | Company name | `Example Inc.` |
| phone | string | optional | Phone number | `123456789` |
| tax_id | string | optional | Tax ID | `123456789` |
| address | object | optional | Address object | |
| password | string | optional | Account password | |
| role_id | integer | optional | Role ID | `1` |
| custom_fields | object | optional | Custom field data | `{}` |
| note | string | optional | Internal note | `Note` |
| optin | string | optional | Marketing consent | `Yes` |
| employee_id | integer | optional | Assigned employee ID | `2` |

#### Address Request Object
| Field | Type | Description |
|-------|------|-------------|
| line_1 | string | Address line 1 |
| line_2 | string | Address line 2 |
| city | string | City |
| state | string | State/Province |
| country | string | Country code |
| postcode | string | Postal code |

### Response Status Codes
| Code | Description |
|------|-------------|
| 201 | Created |
| 400 | Bad Request - Validation error |
| 401 | Unauthorized |

### Response Body Schema (201)
Returns `Client` object (see 17.1 for schema)

### Side Effects / State Changes
- Creates new client user account
- Generates affiliate ID and link
- May send welcome email (not documented)

---

## 17.3 Retrieve a Client

### File Path
`spp-api-documentation/17. Clients/17.3 retrieve-client.md`

### Name
Retrieve a client

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/clients/{client}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| client | integer or allOf | **required** | Client user ID | `1` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |

---

## 17.4 Update a Client

### File Path
`spp-api-documentation/17. Clients/17.4 update-client.md`

### Name
Update a client

### HTTP Method
`PUT`

### URL Path
`https://{workspaceUrl}/api/clients/{client}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| client | integer or allOf | **required** | Client user ID | `1` |

### Request Body Schema
All fields from create are optional for update:
| Field | Type | Description |
|-------|------|-------------|
| email | string | Email address |
| name_f | string | First name |
| name_l | string | Last name |
| company | string | Company name |
| phone | string | Phone number |
| tax_id | string | Tax ID |
| address | object | Address object |
| password | string | New password |
| role_id | integer | Role ID |
| custom_fields | object | Custom field data |
| note | string | Internal note |
| optin | string | Marketing consent |
| employee_id | integer | Assigned employee ID |
| status | integer | Account status |

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |

---

## 17.5 Delete a Client

### File Path
`spp-api-documentation/17. Clients/17.5 delete-client.md`

### Name
Delete a client

### HTTP Method
`DELETE`

### URL Path
`https://{workspaceUrl}/api/clients/{client}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| client | integer or allOf | **required** | Client user ID | `1` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 204 | No Content - Deleted |
| 401 | Unauthorized |
| 404 | Not Found |

### Side Effects / State Changes
- May be soft delete (not documented)
- Associated orders/tickets may remain

---

## Ambiguities and Missing Information

1. **Status Values:** Integer status values not mapped to meanings
2. **Password Requirements:** No password rules documented
3. **Email Uniqueness:** Whether email must be unique not documented
4. **Delete Behavior:** Soft vs hard delete not specified
5. **Custom Fields:** Available custom fields not documented
6. **Role Assignment:** What roles are valid for clients not documented
7. **Team Relationships:** team_owner_ids/team_member_ids usage unclear

---

## Cross-references

- Orders (7. Orders) - `user_id`, `client` object
- Tickets (14. Tickets) - `user_id`, `client` object
- Subscriptions (11. Subscriptions) - `client` object
- Team (13. Team) - `employee_id`, `managers` reference team members
- ClientActivities (16. ClientActivities) - Activities for clients
- MagicLink (6. MagicLink) - Generate login links for clients
