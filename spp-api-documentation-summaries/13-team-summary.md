# 13. Team - API Documentation Summary

## Overview
The Team API provides read-only access to team members (staff users). Team members are users with administrative roles and permissions.

**Note:** No create, update, or delete endpoints exist - team management is read-only via API.

---

## 13.1 List All Team Members

### File Path
`spp-api-documentation/13. Team/13.1 list-team-members.md`

### Name
List all team members

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/team`

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
  "data": [User],
  "links": PaginationLinks,
  "meta": PaginationMeta
}
```

#### User Object (Team Member)
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
| created_at | string\<date-time\> | required | Created timestamp | |

#### Role Object
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| id | integer | required | Role ID | `1` |
| name | string | required | Role name | `Administrator` |
| dashboard_access | integer | required | Dashboard access level | `3` |
| order_access | integer | required | Order access level | `3` |
| order_management | integer | required | Order management level | `3` |
| ticket_access | integer | required | Ticket access level | `3` |
| ticket_management | integer | required | Ticket management level | `3` |
| invoice_access | integer | required | Invoice access level | `3` |
| invoice_management | integer | required | Invoice management level | `3` |
| clients | integer | required | Clients permission | `3` |
| services | integer | required | Services permission | `3` |
| coupons | integer | required | Coupons permission | `3` |
| forms | integer | required | Forms permission | `3` |
| messaging | integer | required | Messaging permission | `3` |
| affiliates | integer | required | Affiliates permission | `3` |
| rank_tracking | integer | required | Rank tracking permission | `3` |
| team | boolean | required | Team permission (deprecated) | `true` |
| settings | boolean | required | Settings permission (deprecated) | `true` |
| settings_company | boolean | required | Company settings | `true` |
| settings_payments | boolean | required | Payment settings | `true` |
| settings_team | boolean | required | Team settings | `true` |
| settings_modules | boolean | required | Module settings | `true` |
| settings_integrations | boolean | required | Integration settings | `true` |
| settings_orders | boolean | required | Order settings | `true` |
| settings_tickets | boolean | required | Ticket settings | `true` |
| settings_accounts | boolean | required | Account settings | `true` |
| settings_messages | boolean | required | Message settings | `true` |
| settings_tags | boolean | required | Tag settings | `true` |
| settings_sidebar | boolean | required | Sidebar settings | `true` |
| settings_dashboard | boolean | required | Dashboard settings | `true` |
| settings_templates | boolean | required | Template settings | `true` |
| settings_emails | boolean | required | Email settings | `true` |
| settings_language | boolean | required | Language settings | `true` |
| settings_logs | boolean | required | Log settings | `true` |
| created_at | string\<date-time\> | required | Created timestamp | |
| updated_at | string\<date-time\> | required | Updated timestamp | |

**Permission Levels:** 0=None, 1=Own, 2=Group, 3=All

### Example Request
```bash
curl --request GET \
  --url https://example.spp.co/api/team \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123'
```

### Notes / Gotchas
- Team members sorted by creation date in descending order
- Same User object structure as Clients but with staff roles
- `team` and `settings` role fields are deprecated

---

## 13.2 Retrieve a Team Member

### File Path
`spp-api-documentation/13. Team/13.2 retrieve-team-member.md`

### Name
Get team member

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/team/{user}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| user | integer or allOf | **required** | User ID | `1` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found (implied) |

### Response Body Schema (200)
Returns `User` object (see 13.1 for schema)

### Example Request
```bash
curl --request GET \
  --url https://example.spp.co/api/team/1 \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123'
```

---

## Ambiguities and Missing Information

1. **No CRUD Operations:** Only list and retrieve endpoints exist
2. **Team vs Client Distinction:** How system determines team vs client not documented
3. **Permission Levels:** Integer values (0-3) explained but edge cases unclear
4. **Status Values:** User status integer values not documented
5. **404 Response:** Retrieve endpoint doesn't explicitly list 404

---

## Cross-references

- Orders (7. Orders) - `employees` array references team members
- OrderTasks (9. OrderTasks) - `employee_ids` for task assignment
- Tickets (14. Tickets) - `employees` array references team members
- Clients (17. Clients) - `employee_id`, `managers` reference team members
- MagicLink (6. MagicLink) - Staff users cannot use magic links
