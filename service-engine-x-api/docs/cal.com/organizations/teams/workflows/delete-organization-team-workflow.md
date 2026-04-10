<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-workflows/delete-organization-team-workflow -->

# Delete organization team workflow

Required membership role: `team admin`. PBAC permission: `workflow.delete`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`DELETE /v2/organizations/{orgId}/teams/{teamId}/workflows/{workflowId}`

**Tags:** Orgs / Teams / Workflows

## Path Parameters

### `teamId` **required**

**Type:** `number`

### `workflowId` **required**

**Type:** `number`

### `orgId` **required**

**Type:** `number`

## Header Parameters

### `Authorization` *optional*

**Type:** `string`

For non-platform customers - value must be `Bearer <token>` where `<token>` is api key prefixed with cal_

### `x-cal-secret-key` *optional*

**Type:** `string`

For platform customers - OAuth client secret key

### `x-cal-client-id` *optional*

**Type:** `string`

For platform customers - OAuth client ID

## Example Request

```bash
curl -X DELETE "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/workflows/{workflowId}" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 200
