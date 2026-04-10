<!-- Source: https://cal.com/docs/api-reference/v2/orgs-attributes/delete-an-attribute -->

# Delete an attribute

`DELETE /v2/organizations/{orgId}/attributes/{attributeId}`

Required membership role: `org admin`. PBAC permission: `organization.attributes.delete`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

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
curl -X DELETE \
  "https://api.cal.com/v2/organizations/<orgId>/attributes/<attributeId>" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13"
```
