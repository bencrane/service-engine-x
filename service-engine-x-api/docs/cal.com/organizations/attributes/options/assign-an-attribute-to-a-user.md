<!-- Source: https://cal.com/docs/api-reference/v2/orgs-attributes-options/assign-an-attribute-to-a-user -->

# Assign an attribute to a user

`POST /v2/organizations/{orgId}/attributes/options/{userId}`

Required membership role: `org admin`. PBAC permission: `organization.attributes.editUsers`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

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
| `userId` | `number` | Yes |  |

## Request Body

- **`value`** (`string`)
- **`attributeOptionId`** (`string`)
- **`attributeId`** **required** (`string`)

### Example Request Body

```json
{
  "value": "string",
  "attributeOptionId": "string",
  "attributeId": "string"
}
```

## Responses

### 201 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`
- **`data`** **required** (`object`)
  - **`id`** **required** (`string`): The ID of the option assigned to the user
  - **`memberId`** **required** (`number`): The ID form the org membership for the user
  - **`attributeOptionId`** **required** (`string`): The value of the option

## Example Request

```bash
curl -X POST \
  "https://api.cal.com/v2/organizations/<orgId>/attributes/options/<userId>" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13" \
  -H "Content-Type: application/json" \
  -d '<request_body>'
```
