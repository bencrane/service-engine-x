<!-- Source: https://cal.com/docs/api-reference/v2/orgs-attributes/create-an-attribute -->

# Create an attribute

`POST /v2/organizations/{orgId}/attributes`

Required membership role: `org admin`. PBAC permission: `organization.attributes.create`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

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

## Request Body

- **`name`** **required** (`string`)
- **`slug`** **required** (`string`)
- **`type`** **required** (`enum`)
  - Enum values: `TEXT`, `NUMBER`, `SINGLE_SELECT`, `MULTI_SELECT`
- **`options`** **required** (`object[]`)
  Array items:
  - **`value`** **required** (`string`)
  - **`slug`** **required** (`string`)
- **`enabled`** (`boolean`)

### Example Request Body

```json
{
  "name": "string",
  "slug": "string",
  "type": "TEXT",
  "options": [
    {
      "value": "string",
      "slug": "string"
    }
  ],
  "enabled": true
}
```

## Responses

### 201 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`
- **`data`** **required** (`object`)
  - **`id`** **required** (`string`): The ID of the attribute
    - Example: `attr_123`
  - **`teamId`** **required** (`number`): The team ID associated with the attribute
    - Example: `1`
  - **`type`** **required** (`enum`): The type of the attribute
    - Enum values: `TEXT`, `NUMBER`, `SINGLE_SELECT`, `MULTI_SELECT`
  - **`name`** **required** (`string`): The name of the attribute
    - Example: `Attribute Name`
  - **`slug`** **required** (`string`): The slug of the attribute
    - Example: `attribute-name`
  - **`enabled`** **required** (`boolean`): Whether the attribute is enabled and displayed on their profile
    - Example: `True`
  - **`usersCanEditRelation`** (`boolean`): Whether users can edit the relation
    - Example: `True`

## Example Request

```bash
curl -X POST \
  "https://api.cal.com/v2/organizations/<orgId>/attributes" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13" \
  -H "Content-Type: application/json" \
  -d '<request_body>'
```
