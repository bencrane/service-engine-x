<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-invite/create-team-invite-link -->

# Create team invite link

Required membership role: `team admin`. PBAC permission: `team.invite`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`POST /v2/organizations/{orgId}/teams/{teamId}/invite`

**Tags:** Orgs / Teams / Invite

## Path Parameters

### `orgId` **required**

**Type:** `number`

### `teamId` **required**

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
curl -X POST "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/invite" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 200

- **`status`** (`"success"` | `"error"`) **required**
  Allowed values: `success`, `error`
- **`data`** (object) **required**
  - **`token`** (string) **required**
    Unique invitation token for this team. Share this token with prospective members to allow them to join the team/organization.
  - **`inviteLink`** (string) **required**
    Complete invitation URL that can be shared with prospective members. Opens the signup page with the token and redirects to getting started after signup.

**Example Response:**

```json
{
  "status": "success",
  "data": {
    "token": "f6a5c8b1d2e34c7f90a1b2c3d4e5f6a5b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2",
    "inviteLink": "http://app.cal.com/signup?token=f6a5c8b1d2e34c7f90a1b2c3d4e5f6a5b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2&callbackUrl=/getting-started"
  }
}
```
