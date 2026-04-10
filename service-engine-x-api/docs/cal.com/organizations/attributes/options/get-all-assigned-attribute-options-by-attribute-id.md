<!-- Source: https://cal.com/docs/api-reference/v2/orgs-attributes-options/get-all-assigned-attribute-options-by-attribute-id -->

# Get all assigned attribute options by attribute ID

`GET /v2/organizations/{orgId}/attributes/{attributeId}/options/assigned`

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

## Query Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `skip` | `number` | No | Number of responses to skip |
| `take` | `number` | No | Number of responses to take |
| `assignedOptionIds` | `string[]` | No | Filter by assigned attribute option ids. ids must be separated by a comma. |
| `teamIds` | `number[]` | No | Filter by teamIds. Team ids must be separated by a comma. |

## Responses

### 200 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`
- **`data`** **required** (`object[]`)
  Array items:
  - **`id`** **required** (`string`): The ID of the option
    - Example: `attr_option_id`
  - **`attributeId`** **required** (`string`): The ID of the attribute
    - Example: `attr_id`
  - **`value`** **required** (`string`): The value of the option
    - Example: `option_value`
  - **`slug`** **required** (`string`): The slug of the option
    - Example: `option-slug`
  - **`assignedUserIds`** **required** (`number[]`): Ids of the users assigned to the attribute option.

## Example Request

```bash
curl -X GET \
  "https://api.cal.com/v2/organizations/<orgId>/attributes/<attributeId>/options/assigned" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13"
```
