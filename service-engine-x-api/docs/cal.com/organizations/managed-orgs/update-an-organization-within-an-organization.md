<!-- Source: https://cal.com/docs/api-reference/v2/managed-orgs/update-an-organization-within-an-organization -->

# Update an organization within an organization

`PATCH /v2/organizations/{orgId}/organizations/{managedOrganizationId}`

For platform, the plan must be 'SCALE' or higher to access this endpoint. Required membership role: `org admin`. PBAC permission: `organization.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

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
| `orgId` | `number` | Yes |  |
| `managedOrganizationId` | `number` | Yes |  |

## Request Body

- **`name`** (`string`): Name of the organization
  - Example: `CalTeam`
- **`metadata`** (`object`): You can store any additional data you want here.
Metadata must have at most 50 keys, each key up to 40 characters.
Values can be strings (up to 500 characters), numbers, or booleans.

### Example Request Body

```json
{
  "name": "CalTeam",
  "metadata": {
    "key": "value"
  }
}
```

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
curl -X PATCH \
  "https://api.cal.com/v2/organizations/<orgId>/organizations/<managedOrganizationId>" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13" \
  -H "Content-Type: application/json" \
  -d '<request_body>'
```
