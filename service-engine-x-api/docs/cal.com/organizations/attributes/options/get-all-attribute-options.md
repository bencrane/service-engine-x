<!-- Source: https://cal.com/docs/api-reference/v2/orgs-attributes-options/get-all-attribute-options -->

# Get all attribute options

`GET /v2/organizations/{orgId}/attributes/{attributeId}/options`

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

## Example Request

```bash
curl -X GET \
  "https://api.cal.com/v2/organizations/<orgId>/attributes/<attributeId>/options" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13"
```
