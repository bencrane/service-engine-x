<!-- Source: https://cal.com/docs/api-reference/v2/managed-orgs/get-an-organization-within-an-organization -->

# Get an organization within an organization

`GET /v2/organizations/{orgId}/organizations/{managedOrganizationId}`

For platform, the plan must be 'SCALE' or higher to access this endpoint. Required membership role: `org admin`. PBAC permission: `organization.read`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Authorization

This endpoint requires authentication with a **Bearer token**.

```
Authorization: Bearer <your_api_key>
```

## Headers

| Name | Required | Description |
|------|----------|-------------|
| `Authorization` | Yes | Bearer token |
| `cal-api-version` | Yes | API version: `2024-08-13` |
| `x-cal-secret-key` | No | For platform customers - OAuth client secret key |
| `x-cal-client-id` | No | For platform customers - OAuth client ID |

## Path Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `managedOrganizationId` | `number` | Yes |  |
| `orgId` | `number` | Yes |  |

## Responses

### 200 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`
- **`data`** **required** (`object`)
  - **`id`** **required** (`number`)
  - **`name`** **required** (`string`)
  - **`slug`** (`string`)
  - **`metadata`** (`object`)

## Example Request

```bash
curl -X GET \
  "https://api.cal.com/v2/organizations/<orgId>/organizations/<managedOrganizationId>" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13"
```
