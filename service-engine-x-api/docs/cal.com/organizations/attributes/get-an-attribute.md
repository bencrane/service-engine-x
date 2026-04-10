<!-- Source: https://cal.com/docs/api-reference/v2/orgs-attributes/get-an-attribute -->

# Get an attribute

`GET /v2/organizations/{orgId}/attributes/{attributeId}`

Required membership role: `org member`. PBAC permission: `organization.attributes.read`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

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

## Path Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `orgId` | `number` | Yes |  |
| `attributeId` | `string` | Yes |  |

## Responses

### 200 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`
- **`data`** **required** (`object`)

## Example Request

```bash
curl -X GET \
  "https://api.cal.com/v2/organizations/<orgId>/attributes/<attributeId>" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13"
```
