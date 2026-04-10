<!-- Source: https://cal.com/docs/api-reference/v2/managed-orgs/create-an-organization-within-an-organization -->

# Create an organization within an organization

`POST /v2/organizations/{orgId}/organizations`

For platform, the plan must be 'SCALE' or higher to access this endpoint. Required membership role: `org admin`. PBAC permission: `organization.create`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

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

## Request Body

- **`apiKeyDaysValid`** (`number`): For how many days is managed organization api key valid. Defaults to 30 days.
  - Default: `30`
  - Example: `60`
- **`apiKeyNeverExpires`** (`boolean`): If true, organization api key never expires.
  - Example: `True`
- **`name`** **required** (`string`): Name of the organization
  - Example: `CalTeam`
- **`slug`** (`string`): Organization slug in kebab-case - if not provided will be generated automatically based on name.
  - Example: `cal-tel`
- **`metadata`** (`object`): You can store any additional data you want here.
Metadata must have at most 50 keys, each key up to 40 characters.
Values can be strings (up to 500 characters), numbers, or booleans.

### Example Request Body

```json
{
  "apiKeyDaysValid": 60,
  "apiKeyNeverExpires": true,
  "name": "CalTeam",
  "slug": "cal-tel",
  "metadata": {
    "key": "value"
  }
}
```

## Responses

### 201 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`
- **`data`** **required** (`object`)
  - **`id`** **required** (`number`)
  - **`name`** **required** (`string`)
  - **`slug`** (`string`)
  - **`metadata`** (`object`)
  - **`apiKey`** **required** (`string`)

## Example Request

```bash
curl -X POST \
  "https://api.cal.com/v2/organizations/<orgId>/organizations" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13" \
  -H "Content-Type: application/json" \
  -d '<request_body>'
```
