<!-- Source: https://cal.com/docs/api-reference/v2/managed-orgs/get-all-organizations-within-an-organization -->

# Get all organizations within an organization

`GET /v2/organizations/{orgId}/organizations`

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
| `orgId` | `number` | Yes |  |

## Query Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `take` | `number` | No | Maximum number of items to return Default: `250` |
| `skip` | `number` | No | Number of items to skip Default: `0` |
| `slug` | `string` | No | The slug of the managed organization |
| `metadataKey` | `string` | No | The key of the metadata - it is case sensitive so provide exactly as stored. If you provide it then you must also provide metadataValue |
| `metadataValue` | `string` | No | The value of the metadata - it is case sensitive so provide exactly as stored. If you provide it then you must also provide metadataKey |

## Responses

### 200 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`
- **`data`** **required** (`object[]`)
  Array items:
  - **`id`** **required** (`number`)
  - **`name`** **required** (`string`)
  - **`slug`** (`string`)
  - **`metadata`** (`object`)
- **`pagination`** **required** (`object`)
  - **`totalItems`** **required** (`number`): The total number of items available across all pages, matching the query criteria.
    - Example: `123`
  - **`remainingItems`** **required** (`number`): The number of items remaining to be fetched *after* the current page. Calculated as: `totalItems - (skip + itemsPerPage)`.
    - Example: `103`
  - **`returnedItems`** **required** (`number`): The number of items returned in the current page.
    - Example: `10`
  - **`itemsPerPage`** **required** (`number`): The maximum number of items requested per page.
    - Example: `10`
  - **`currentPage`** **required** (`number`): The current page number being returned.
    - Example: `2`
  - **`totalPages`** **required** (`number`): The total number of pages available.
    - Example: `13`
  - **`hasNextPage`** **required** (`boolean`): Indicates if there is a subsequent page available after the current one.
    - Example: `True`
  - **`hasPreviousPage`** **required** (`boolean`): Indicates if there is a preceding page available before the current one.
    - Example: `True`

## Example Request

```bash
curl -X GET \
  "https://api.cal.com/v2/organizations/<orgId>/organizations" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13"
```
