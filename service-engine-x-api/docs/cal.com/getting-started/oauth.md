<!-- Source: https://cal.com/docs/api-reference/v2/oauth -->

# OAuth - Cal.com Docs

Getting Started
# OAuth
Copy page

Authorize apps with Cal.com accounts using OAuthCopy pageAs an example, you can view our OAuth flow in action on Zapier. Try to connect your Cal.com account here. To enable OAuth in one of your apps, you will need a Client ID, Client Secret, Authorization URL, Access Token Request URL, and Refresh Token Request URL.

#### ​Get your OAuth “Continue with Cal.com” Badge

- https://app.cal.com/continue-with-calcom-coss-ui.svg

- https://app.cal.com/continue-with-calcom-dark-rounded.svg

- https://app.cal.com/continue-with-calcom-dark-squared.svg

- https://app.cal.com/continue-with-calcom-light-rounded.svg

- https://app.cal.com/continue-with-calcom-light-squared.svg

- https://app.cal.com/continue-with-calcom-neutral-rounded.svg

- https://app.cal.com/continue-with-calcom-light-squared.svg

## ​1. OAuth Client Credentials

You can create an OAuth client via the following page https://app.cal.com/settings/developer/oauth. The OAuth client will be in a “pending” state
and not yet ready to use. You must select at least one scope when creating the OAuth client. You can register up to 10 redirect URIs per OAuth client.
An admin from Cal.com will then review your OAuth client and you will receive an email if it was accepted or rejected. If it was accepted then your OAuth client
is ready to be used.

### ​Available Scopes

Scopes control which API endpoints the OAuth token can access. Once a user authorizes your client with a given set of scopes, the issued access token can only be used to call endpoints covered by those scopes — any request to an endpoint outside the granted scopes will be rejected. The following scopes are available:
ScopeDescriptionEndpoints`EVENT_TYPE_READ`View event typesGet all event types, 
 Get an event type, 
 Get event type private links, 
 `GET /v2/event-types/:eventTypeId/webhooks`, 
 `GET /v2/event-types/:eventTypeId/webhooks/:webhookId``EVENT_TYPE_WRITE`Create, edit, and delete event typesCreate an event type, 
 Update an event type, 
 Delete an event type, 
 Create a private link, 
 Update a private link, 
 Delete a private link, 
 `POST /v2/event-types/:eventTypeId/webhooks`, 
 `PATCH /v2/event-types/:eventTypeId/webhooks/:webhookId`, 
 `DELETE /v2/event-types/:eventTypeId/webhooks/:webhookId`, 
 `DELETE /v2/event-types/:eventTypeId/webhooks``BOOKING_READ`View bookingsGet all bookings, 
 Get booking recordings, 
 Get transcript download links, 
 Get calendar links, 
 Get booking references, 
 Get conferencing sessions, 
 `GET /v2/bookings/:bookingUid/attendees`, 
 `GET /v2/bookings/:bookingUid/attendees/:attendeeId``BOOKING_WRITE`Create, edit, and delete bookingsAdd guests to a booking, 
 Update booking location, 
 Mark a booking absence, 
 Reassign to auto-selected host, 
 Reassign to a specific host, 
 Confirm a booking, 
 Decline a booking, 
 `POST /v2/bookings/:bookingUid/attendees``SCHEDULE_READ`View availabilityGet all schedules, 
 Get a schedule, 
 Get default schedule, 
 `GET /v2/me/ooo``SCHEDULE_WRITE`Create, edit, and delete availabilityCreate a schedule, 
 Update a schedule, 
 Delete a schedule, 
 `POST /v2/me/ooo`, 
 `PATCH /v2/me/ooo/:oooId`, 
 `DELETE /v2/me/ooo/:oooId``APPS_READ`View connected appsGet all calendars, 
 Get busy times, 
 Check an ICS feed, 
 Check a calendar connection, 
 `GET /v2/conferencing`, 
 `GET /v2/conferencing/default``APPS_WRITE`Connect and disconnect appsSave an ICS feed, 
 Get OAuth connect URL, 
 Save Apple calendar credentials, 
 Disconnect a calendar, 
 `POST /v2/conferencing/:app/connect`, 
 `GET /v2/conferencing/:app/oauth/auth-url`, 
 `POST /v2/conferencing/:app/default`, 
 `DELETE /v2/conferencing/:app/disconnect`, 
 `POST /v2/selected-calendars`, 
 `DELETE /v2/selected-calendars`, 
 `PUT /v2/destination-calendars``PROFILE_READ`View personal infoGet my profile`PROFILE_WRITE`Edit personal infoUpdate my profile
Some endpoints like `POST /v2/bookings` (create), `POST /v2/bookings/:bookingUid/cancel` (cancel), `POST /v2/bookings/:bookingUid/reschedule` (reschedule), and slot availability endpoints are public and do not require any scope. You can still pass an OAuth access token when calling these endpoints — the token is accepted but not required. This means you can use a consistent `Authorization: Bearer <token>` header across all API requests without worrying about whether a specific endpoint is public or scoped.

### ​Team Scopes

Team scopes control access to team-level resources. These are used for endpoints under `/v2/teams/:teamId/...` and `/v2/organizations/:orgId/teams/:teamId/...`.
ScopeDescriptionEndpoints`TEAM_EVENT_TYPE_READ`View team event types`GET /v2/teams/:teamId/event-types`, 
 `GET /v2/teams/:teamId/event-types/:eventTypeId`, 
 `GET /v2/organizations/:orgId/teams/:teamId/event-types`, 
 `GET /v2/organizations/:orgId/teams/:teamId/event-types/:eventTypeId`, 
 `GET /v2/teams/:teamId/event-types/:eventTypeId/webhooks`, 
 `GET /v2/teams/:teamId/event-types/:eventTypeId/webhooks/:webhookId`, 
 `GET /v2/organizations/:orgId/teams/:teamId/event-types/:eventTypeId/private-links``TEAM_EVENT_TYPE_WRITE`Create, edit, and delete team event types`POST /v2/teams/:teamId/event-types`, 
 `PATCH /v2/teams/:teamId/event-types/:eventTypeId`, 
 `DELETE /v2/teams/:teamId/event-types/:eventTypeId`, 
 `POST /v2/teams/:teamId/event-types/:eventTypeId/create-phone-call`, 
 `POST /v2/organizations/:orgId/teams/:teamId/event-types`, 
 `PATCH /v2/organizations/:orgId/teams/:teamId/event-types/:eventTypeId`, 
 `DELETE /v2/organizations/:orgId/teams/:teamId/event-types/:eventTypeId`, 
 `POST /v2/organizations/:orgId/teams/:teamId/event-types/:eventTypeId/create-phone-call`, 
 `POST /v2/teams/:teamId/event-types/:eventTypeId/webhooks`, 
 `PATCH /v2/teams/:teamId/event-types/:eventTypeId/webhooks/:webhookId`, 
 `DELETE /v2/teams/:teamId/event-types/:eventTypeId/webhooks/:webhookId`, 
 `DELETE /v2/teams/:teamId/event-types/:eventTypeId/webhooks`, 
 `POST /v2/organizations/:orgId/teams/:teamId/event-types/:eventTypeId/private-links`, 
 `PATCH /v2/organizations/:orgId/teams/:teamId/event-types/:eventTypeId/private-links/:linkId`, 
 `DELETE /v2/organizations/:orgId/teams/:teamId/event-types/:eventTypeId/private-links/:linkId``TEAM_BOOKING_READ`View team bookings`GET /v2/teams/:teamId/bookings`, 
 `GET /v2/organizations/:orgId/teams/:teamId/bookings`, 
 `GET /v2/organizations/:orgId/teams/:teamId/bookings/:bookingUid/references``TEAM_BOOKING_WRITE`Create, edit, and delete team bookingsNo endpoints currently use this scope`TEAM_SCHEDULE_READ`View team schedules`GET /v2/teams/:teamId/schedules`, 
 `GET /v2/organizations/:orgId/teams/:teamId/schedules`, 
 `GET /v2/organizations/:orgId/teams/:teamId/users/:userId/schedules`, 
 `GET /v2/teams/:teamId/users/:userId/ooo``TEAM_SCHEDULE_WRITE`Create, edit, and delete team schedules`POST /v2/teams/:teamId/users/:userId/ooo`, 
 `PATCH /v2/teams/:teamId/users/:userId/ooo/:oooId`, 
 `DELETE /v2/teams/:teamId/users/:userId/ooo/:oooId``TEAM_PROFILE_READ`View team profiles`GET /v2/teams`, 
 `GET /v2/teams/:teamId`, 
 `GET /v2/organizations/:orgId/teams/:teamId``TEAM_PROFILE_WRITE`Create, edit, and delete teams`POST /v2/teams`, 
 `PATCH /v2/teams/:teamId`, 
 `DELETE /v2/teams/:teamId``TEAM_MEMBERSHIP_READ`View team memberships`GET /v2/teams/:teamId/memberships`, 
 `GET /v2/teams/:teamId/memberships/:membershipId`, 
 `GET /v2/organizations/:orgId/teams/:teamId/memberships`, 
 `GET /v2/organizations/:orgId/teams/:teamId/memberships/:membershipId``TEAM_MEMBERSHIP_WRITE`Create, edit, and delete team memberships`POST /v2/teams/:teamId/memberships`, 
 `PATCH /v2/teams/:teamId/memberships/:membershipId`, 
 `DELETE /v2/teams/:teamId/memberships/:membershipId`, 
 `POST /v2/teams/:teamId/invite`, 
 `POST /v2/organizations/:orgId/teams/:teamId/memberships`, 
 `PATCH /v2/organizations/:orgId/teams/:teamId/memberships/:membershipId`, 
 `DELETE /v2/organizations/:orgId/teams/:teamId/memberships/:membershipId`, 
 `POST /v2/organizations/:orgId/teams/:teamId/invite`

### ​Organization Scopes

Organization scopes control access to organization-wide resources. These are used for endpoints under `/v2/organizations/:orgId/...` that do not target a specific team.
An `ORG_` scope automatically grants the corresponding `TEAM_` scope. For example, a token with `ORG_PROFILE_READ` can also access endpoints that require `TEAM_PROFILE_READ`.
ScopeDescriptionEndpoints`ORG_EVENT_TYPE_READ`View all event types across the organization`GET /v2/organizations/:orgId/teams/event-types``ORG_EVENT_TYPE_WRITE`Create, edit, and delete event types across the organizationNo endpoints currently use this scope`ORG_BOOKING_READ`View all bookings across the organization`GET /v2/organizations/:orgId/bookings``ORG_BOOKING_WRITE`Create, edit, and delete bookings across the organizationNo endpoints currently use this scope`ORG_SCHEDULE_READ`View schedules across the organization`GET /v2/organizations/:orgId/schedules`, 
 `GET /v2/organizations/:orgId/users/:userId/schedules`, 
 `GET /v2/organizations/:orgId/users/:userId/schedules/:scheduleId`, 
 `GET /v2/organizations/:orgId/users/:userId/ooo`, 
 `GET /v2/organizations/:orgId/ooo``ORG_SCHEDULE_WRITE`Create, edit, and delete schedules across the organization`POST /v2/organizations/:orgId/users/:userId/schedules`, 
 `PATCH /v2/organizations/:orgId/users/:userId/schedules/:scheduleId`, 
 `DELETE /v2/organizations/:orgId/users/:userId/schedules/:scheduleId`, 
 `POST /v2/organizations/:orgId/users/:userId/ooo`, 
 `PATCH /v2/organizations/:orgId/users/:userId/ooo/:oooId`, 
 `DELETE /v2/organizations/:orgId/users/:userId/ooo/:oooId``ORG_PROFILE_READ`View organization teams`GET /v2/organizations/:orgId/teams`, 
 `GET /v2/organizations/:orgId/teams/me``ORG_PROFILE_WRITE`Create, edit, and delete organization teams`POST /v2/organizations/:orgId/teams`, 
 `PATCH /v2/organizations/:orgId/teams/:teamId`, 
 `DELETE /v2/organizations/:orgId/teams/:teamId``ORG_MEMBERSHIP_READ`View organization memberships and users`GET /v2/organizations/:orgId/memberships`, 
 `GET /v2/organizations/:orgId/memberships/:membershipId`, 
 `GET /v2/organizations/:orgId/users``ORG_MEMBERSHIP_WRITE`Create, edit, and delete organization memberships and users`POST /v2/organizations/:orgId/memberships`, 
 `PATCH /v2/organizations/:orgId/memberships/:membershipId`, 
 `DELETE /v2/organizations/:orgId/memberships/:membershipId`, 
 `POST /v2/organizations/:orgId/users`, 
 `PATCH /v2/organizations/:orgId/users/:userId`, 
 `DELETE /v2/organizations/:orgId/users/:userId`

## ​2. Authorize

To initiate the OAuth flow, direct users to the following authorization URL:
`https://app.cal.com/auth/oauth2/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&state=YOUR_STATE&scope=BOOKING_READ%20BOOKING_WRITE`
**URL Parameters:**
ParameterRequiredDescription`client_id`YesYour OAuth client ID`redirect_uri`YesWhere users will be redirected after authorization. Must exactly match one of the registered redirect URIs.`state`RecommendedA securely generated random string to mitigate CSRF attacks`scope`YesSpace or comma-separated list of scopes to request (e.g. `BOOKING_READ BOOKING_WRITE` or `BOOKING_READ,BOOKING_WRITE`). Must be a subset of scopes enabled on the OAuth client.`code_challenge`For public clientsPKCE code challenge (S256 method)
After users click **Allow**, they will be redirected to the `redirect_uri` with `code` (authorization code) and `state` as URL parameters:

```
`https://your-app.com/callback?code=AUTHORIZATION_CODE&state=YOUR_STATE
`
```

#### ​Error Handling

Errors during the authorization step are displayed directly to the user on the Cal.com authorization page. Your application will not receive a JSON error response for these cases:

- **Client not found**: No OAuth client exists with the provided `client_id`.

- **Client not approved**: The OAuth client has not been approved by a Cal.com admin yet.

- **Mismatched redirect URI**: The `redirect_uri` does not match any of the registered redirect URIs for the OAuth client.

If an error occurs after the client is validated, the user is redirected to the `redirect_uri` with an error:

- **Scope required**: If the `scope` parameter is missing, the error `scope parameter is required for this OAuth client` is displayed on the authorization page.

- **Unknown scope**: If the `scope` parameter includes scope values that do not exist, the user is redirected with `error=invalid_scope` and `error_description=Requested scope is not a recognized scope`. This applies to both regular and legacy clients.

- **Invalid scope**: If the `scope` parameter includes scopes not enabled on the OAuth client, the user is redirected with `error=invalid_request` and `error_description=Requested scope exceeds the client's registered scopes`.

- **Access denied**: If the user denies access or has insufficient permissions, the user is redirected with an error.

```
`https://your-app.com/callback?error=invalid_request&error_description=Requested+scope+exceeds+the+client%27s+registered+scopes&state=YOUR_STATE
`
```

## ​3. Exchange Token

Exchange an authorization code for access and refresh tokens. The token endpoint also accepts `application/x-www-form-urlencoded` content type.
**Endpoint:** `POST https://api.cal.com/v2/auth/oauth2/token`

### ​3.1 Confidential Clients

Confidential clients authenticate with a `client_secret`. All parameters are required:
ParameterDescription`client_id`Your OAuth client ID`client_secret`Your OAuth client secret`grant_type`Must be `authorization_code``code`The authorization code received in the redirect URI`redirect_uri`Must match the redirect URI used in the authorization request

-  cURL
-  fetch
-  axios
```
`curl -X POST https://api.cal.com/v2/auth/oauth2/token \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "grant_type": "authorization_code",
    "code": "AUTHORIZATION_CODE",
    "redirect_uri": "https://your-app.com/callback"
  }'
`
```

```
`const response = await fetch("https://api.cal.com/v2/auth/oauth2/token", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    client_id: "YOUR_CLIENT_ID",
    client_secret: "YOUR_CLIENT_SECRET",
    grant_type: "authorization_code",
    code: "AUTHORIZATION_CODE",
    redirect_uri: "https://your-app.com/callback",
  }),
});

const tokens = await response.json();
`
```

```
`import axios from "axios";

const { data } = await axios.post(
  "https://api.cal.com/v2/auth/oauth2/token",
  {
    client_id: "YOUR_CLIENT_ID",
    client_secret: "YOUR_CLIENT_SECRET",
    grant_type: "authorization_code",
    code: "AUTHORIZATION_CODE",
    redirect_uri: "https://your-app.com/callback",
  }
);
`
```

### ​3.2 Public Clients (PKCE)

Public clients (e.g. single-page apps, mobile apps) use PKCE instead of a `client_secret`. You must have sent a `code_challenge` during the authorization step. All parameters are required:
ParameterDescription`client_id`Your OAuth client ID`grant_type`Must be `authorization_code``code`The authorization code received in the redirect URI`redirect_uri`Must match the redirect URI used in the authorization request`code_verifier`The original PKCE code verifier used to generate the `code_challenge`

-  cURL
-  fetch
-  axios
```
`curl -X POST https://api.cal.com/v2/auth/oauth2/token \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "YOUR_CLIENT_ID",
    "grant_type": "authorization_code",
    "code": "AUTHORIZATION_CODE",
    "redirect_uri": "https://your-app.com/callback",
    "code_verifier": "YOUR_CODE_VERIFIER"
  }'
`
```

```
`const response = await fetch("https://api.cal.com/v2/auth/oauth2/token", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    client_id: "YOUR_CLIENT_ID",
    grant_type: "authorization_code",
    code: "AUTHORIZATION_CODE",
    redirect_uri: "https://your-app.com/callback",
    code_verifier: "YOUR_CODE_VERIFIER",
  }),
});

const tokens = await response.json();
`
```

```
`import axios from "axios";

const { data } = await axios.post(
  "https://api.cal.com/v2/auth/oauth2/token",
  {
    client_id: "YOUR_CLIENT_ID",
    grant_type: "authorization_code",
    code: "AUTHORIZATION_CODE",
    redirect_uri: "https://your-app.com/callback",
    code_verifier: "YOUR_CODE_VERIFIER",
  }
);
`
```

#### ​Success Response (200)

```
`{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800,
  "scope": "BOOKING_READ BOOKING_WRITE"
}
`
```

Access tokens expire after 30 minutes (`expires_in: 1800`). Use the refresh token to obtain a new access token. The `scope` field contains the granted scopes as a space-separated string.

#### ​Error Responses

Error responses include `error` and `error_description` fields.

Invalid or expired authorization code (400)
```
`{
  "error": "invalid_grant",
  "error_description": "code_invalid_or_expired"
}
`
```
The authorization code has already been used, has expired, or is invalid. Request a new authorization code.

Invalid client credentials (401)
```
`{
  "error": "invalid_client",
  "error_description": "invalid_client_credentials"
}
`
```
The `client_secret` does not match the `client_id`. Verify your credentials.

Client not found (401)
```
`{
  "error": "invalid_client",
  "error_description": "client_not_found"
}
`
```
No OAuth client exists with the provided `client_id`.

Missing client_id (400)
```
`{
  "error": "invalid_request",
  "error_description": "client_id is required"
}
`
```
The `client_id` field is missing from the request body.

Invalid grant_type (400)
```
`{
  "error": "invalid_request",
  "error_description": "grant_type must be 'authorization_code' or 'refresh_token'"
}
`
```
The `grant_type` field must be either `authorization_code` or `refresh_token`.

## ​4. Refresh Token

Refresh an expired access token using a refresh token.
**Endpoint:** `POST https://api.cal.com/v2/auth/oauth2/token`

### ​4.1 Confidential Clients

Confidential clients authenticate with a `client_secret`. All parameters are required:
ParameterDescription`client_id`Your OAuth client ID`client_secret`Your OAuth client secret`grant_type`Must be `refresh_token``refresh_token`The refresh token received from a previous token response

-  cURL
-  fetch
-  axios
```
`curl -X POST https://api.cal.com/v2/auth/oauth2/token \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "grant_type": "refresh_token",
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
`
```

```
`const response = await fetch("https://api.cal.com/v2/auth/oauth2/token", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    client_id: "YOUR_CLIENT_ID",
    client_secret: "YOUR_CLIENT_SECRET",
    grant_type: "refresh_token",
    refresh_token: "YOUR_REFRESH_TOKEN",
  }),
});

const tokens = await response.json();
`
```

```
`import axios from "axios";

const { data } = await axios.post(
  "https://api.cal.com/v2/auth/oauth2/token",
  {
    client_id: "YOUR_CLIENT_ID",
    client_secret: "YOUR_CLIENT_SECRET",
    grant_type: "refresh_token",
    refresh_token: "YOUR_REFRESH_TOKEN",
  }
);
`
```

### ​4.2 Public Clients

Public clients do not use a `client_secret`. All parameters are required:
ParameterDescription`client_id`Your OAuth client ID`grant_type`Must be `refresh_token``refresh_token`The refresh token received from a previous token response

-  cURL
-  fetch
-  axios
```
`curl -X POST https://api.cal.com/v2/auth/oauth2/token \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "YOUR_CLIENT_ID",
    "grant_type": "refresh_token",
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
`
```

```
`const response = await fetch("https://api.cal.com/v2/auth/oauth2/token", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    client_id: "YOUR_CLIENT_ID",
    grant_type: "refresh_token",
    refresh_token: "YOUR_REFRESH_TOKEN",
  }),
});

const tokens = await response.json();
`
```

```
`import axios from "axios";

const { data } = await axios.post(
  "https://api.cal.com/v2/auth/oauth2/token",
  {
    client_id: "YOUR_CLIENT_ID",
    grant_type: "refresh_token",
    refresh_token: "YOUR_REFRESH_TOKEN",
  }
);
`
```

#### ​Success Response (200)

```
`{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800,
  "scope": "BOOKING_READ BOOKING_WRITE"
}
`
```

Scopes are preserved from the original authorization. You do not need to re-request scopes when refreshing tokens.

#### ​Error Responses

Invalid refresh token (400)
```
`{
  "error": "invalid_grant",
  "error_description": "invalid_refresh_token"
}
`
```
The refresh token is invalid, expired, or malformed. The user must re-authorize.

Invalid client credentials (401)
```
`{
  "error": "invalid_client",
  "error_description": "invalid_client_credentials"
}
`
```
The `client_secret` does not match the `client_id`.

Client not found (401)
```
`{
  "error": "invalid_client",
  "error_description": "client_not_found"
}
`
```
No OAuth client exists with the provided `client_id`.

## ​5. Client Secret Rotation

Cal.com supports rotating client secrets with zero downtime. You can have up to **2 active secrets** at a time, allowing you to deploy a new secret before revoking the old one.

### ​Why rotate secrets?

- A secret may have been accidentally exposed or compromised

- Your security policy requires periodic credential rotation

- An employee with access to the secret has left your organization

### ​How it works

- **Generate a new secret** from your OAuth client settings. Your old secret continues to work — both secrets are valid simultaneously.

- **Update your application** to use the new secret in all token exchange and refresh requests.

- **Verify** that your application works correctly with the new secret.

- **Revoke the old secret** from the settings page. Any requests using the old secret will immediately fail.

### ​Important notes

- You can have a **maximum of 2 secrets** per client. To generate a new one when you already have 2, revoke an existing secret first.

- New secrets are shown **only once** when generated. Copy and store them securely.

- Revoking a secret takes effect **immediately** — there is no grace period.

- **Existing access and refresh tokens remain valid** after secret rotation. Rotation only affects token exchange and refresh requests that require `client_secret`.

- Secret rotation applies only to **confidential clients**. Public clients (PKCE) do not use client secrets.

### ​What needs to change in your code

When you rotate a secret, update the `client_secret` parameter in these requests:
RequestAffected?Authorization redirect (Step 2)No — uses only `client_id`Exchange code for tokens (Step 3)**Yes** — update `client_secret`Refresh access token (Step 4)**Yes** — update `client_secret`API calls with Bearer token (Step 5)No — uses access token

## ​Legacy Client Migration

If your OAuth client was created before scopes were introduced, it is considered a **legacy client**. A client is treated as legacy if it has no scopes configured, or if it only has the old legacy scope values (`READ_BOOKING` and/or `READ_PROFILE`). Access tokens issued by legacy clients can access any resource on behalf of the authorizing user — scopes are not enforced.
You can migrate a legacy client to use explicit scopes without creating a new client. **Order matters** — follow these steps to avoid breaking existing integrations:

### ​Step 1: Update your authorization URL

Add a `scope` query parameter to your authorization URL **before** changing any client settings. Legacy clients skip scope validation during authorization, so users can already authorize with a scope parameter even while the client is still in legacy mode.

```
`https://app.cal.com/auth/oauth2/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&state=YOUR_STATE&scope=BOOKING_READ%20BOOKING_WRITE
`
```

New access tokens issued after this change will carry only the scopes you specified. For the full list of available scopes, see Available Scopes.

### ​Step 2: Update client scopes in settings

Once your authorization URL is updated and you have verified that new tokens are being issued with the correct scopes, open your OAuth client settings and select the matching scopes. Save the client.
After this step, the client is no longer treated as a legacy client. Scope validation is enforced for all new authorization requests.
Do **not** update the client scopes before updating your authorization URL. Doing so will immediately break the authorization flow for any user who visits the old URL without a `scope` parameter.

### ​Existing tokens

Tokens issued before the migration continue to work until users re-authorize. There is no forced invalidation of existing tokens during the migration.

### ​Re-approval

Changing properties below will trigger a re-review by Cal.com admins and set client to a “pending” state:

- Name

- Logo

- Website URL

- Redirect URI

- Scope expansion (adding new scopes that the client did not previously have)

While pending, the client can only be used by the client owner for testing — other users cannot authorize with it.
Changing properties below will NOT trigger a re-review and client will remain in the state it is:

- Adding a `_READ` scope when the corresponding `_WRITE` scope is already granted (e.g. adding `BOOKING_READ` when `BOOKING_WRITE` is already present)

- Removing scopes

- Purpose description change

- Updating scopes on a legacy client, as long as only user-level scopes are added — adding `TEAM_` or `ORG_` scopes to a legacy client will trigger re-approval. See Legacy Client Migration for details.

## ​6. Verify Access Token

To verify the correct setup and functionality of OAuth credentials, use the following endpoint:
**Endpoint:** `GET https://api.cal.com/v2/me`

-  cURL
-  fetch
-  axios
```
`curl -X GET https://api.cal.com/v2/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
`
```

```
`const response = await fetch("https://api.cal.com/v2/me", {
  headers: { Authorization: "Bearer YOUR_ACCESS_TOKEN" },
});

const user = await response.json();
`
```

```
`import axios from "axios";

const { data } = await axios.get("https://api.cal.com/v2/me", {
  headers: { Authorization: "Bearer YOUR_ACCESS_TOKEN" },
});
`
```

## ​7. Onboarding Embed

The `<OnboardingEmbed />` React component lets you embed Cal.com account creation, onboarding, and OAuth authorization directly inside your application. Users create a real Cal.com account, complete onboarding, and grant your app OAuth access — all without leaving your site. The component
also has an inbuilt “dark” and “light” theme.
The component supports two modes for receiving the authorization code:

- **Callback mode** — provide `onAuthorizationAllowed` to receive the authorization code via a callback. No page navigation occurs.

- **Redirect mode** — don’t provide `onAuthorizationAllowed` and the browser navigates to your `redirectUri` with the code as a query parameter. Works like a standard OAuth redirect.

```
`npm install @calcom/atoms
`
```

### ​Callback Mode

Provide `onAuthorizationAllowed` to receive the authorization code directly. The dialog closes and your callback fires after user authorizes your OAuth client — no page reload.

```
`import { OnboardingEmbed } from "@calcom/atoms";
import { useState } from "react";

function App() {
  const [state] = useState(() => crypto.randomUUID());

  return (
    <OnboardingEmbed
      oAuthClientId="your_client_id"
      authorization={{
        scope: ["BOOKING_READ", "BOOKING_WRITE", "PROFILE_READ"],
        redirectUri: "https://your-app.com/cal/callback",
        state,
      }}
      onAuthorizationAllowed={({ code }) => {
        fetch("/api/cal/exchange", {
          method: "POST",
          body: JSON.stringify({ code, state }),
        });
      }}
      onError={(error) => console.error(error.code, error.message)}
      onClose={() => console.log("Dialog dismissed")}
    />
  );
}
`
```

### ​Redirect Mode

Omit `onAuthorizationAllowed` and the browser navigates to your `redirectUri` after the user completes onboarding and grants access:

```
`https://your-app.com/cal/callback?code=AUTHORIZATION_CODE&state=YOUR_STATE
`
```

```
`import { OnboardingEmbed } from "@calcom/atoms";
import { useState } from "react";

function App() {
  const [state] = useState(() => crypto.randomUUID());

  return (
    <OnboardingEmbed
      oAuthClientId="your_client_id"
      authorization={{
        scope: ["BOOKING_READ", "BOOKING_WRITE", "PROFILE_READ"],
        redirectUri: "https://your-app.com/cal/callback",
        state,
      }}
      onError={(error) => console.error(error.code, error.message)}
    />
  );
}
`
```

### ​Props

PropTypeRequiredDescription`oAuthClientId``string`YesYour OAuth client ID from Section 1.`host``string`NoCal.com host URL. Defaults to `https://app.cal.com`. Used for local development to point to cal web app.`theme``"light" | "dark"`NoTheme for the embedded onboarding UI. Defaults to `"light"`.`user``{ email?: string, name?: string, username?: string }`NoPrefill user details in signup and profile steps.`authorization``AuthorizationProps`YesOAuth authorization parameters (see below).`onAuthorizationAllowed``(result: { code: string }) => void`NoCalled with the authorization code on completion. If provided, enables callback mode. If omitted, enables redirect mode (browser navigates to `redirectUri`).`onError``(error: OnboardingError) => void`NoCalled on unrecoverable error.`onAuthorizationDenied``() => void`NoCalled when the user declines OAuth authorization. If provided, the callback fires and the dialog closes. If omitted, the browser navigates to `redirectUri?error=access_denied&state=YOUR_STATE`.`onClose``() => void`NoCalled when the user dismisses the dialog before completing.`trigger``ReactNode`NoCustom trigger element. Defaults to a “Continue with Cal.com” button.

### ​Authorization Props

PropTypeRequiredDescription`redirectUri``string`YesOne of the redirect URIs registered on your OAuth client. The server validates this against the client’s registered URIs. **Must share the same origin** (scheme + domain + port) **as the page hosting the `<OnboardingEmbed />`**, because the iframe uses `postMessage` with this origin for secure communication. For example, if your OAuth client has redirect URI `https://your-app.com/cal/callback`, then pass it here exactly the same `https://your-app.com/cal/callback`.`scope``string[]`YesOAuth scopes to request. Must be a subset of scopes registered on the OAuth client. See Available Scopes.`state``string`YesCSRF token. Generate a unique value per session and verify it matches when you receive the authorization code.`codeChallenge``string`For public clientsPKCE code challenge (S256 method). Required for public OAuth clients. Generate a `code_verifier` (random 32-byte base64url string), hash it with SHA-256, and pass the result here. Store the `code_verifier` — you’ll need it to exchange the authorization code for tokens.
If the user signs up via Google, the `user` prop values are ignored — name, email, and username are inferred from the Google account instead.

### ​Trigger and Theme

The `theme` prop controls the appearance of the trigger button, the onboarding steps, and the authorization page. The default trigger renders a “Continue with Cal.com” button:
Light theme (default)Dark theme
You can pass a custom trigger element via the `trigger` prop:

```
`<OnboardingEmbed
  trigger={<button>Connect calendar</button>}
  // ...
/>
`
```

### ​Walkthrough — Callback Mode

Here’s what happens when a user clicks the trigger with `onAuthorizationAllowed` provided and the `user` prop set:

```
`<OnboardingEmbed
  oAuthClientId="your_client_id"
  theme="light"
  user={{ email: "[email protected]", name: "Bob", username: "bob100" }}
  authorization={{
    scope: ["EVENT_TYPE_READ"],
    redirectUri: "https://your-app.com/cal/callback",
    state,
  }}
  onAuthorizationAllowed={({ code }) => {
    alert(`Success! Auth code: ${code}`);
  }}
/>
`
```

**1. Trigger** — The component renders a “Continue with Cal.com” button. The user clicks it to open the onboarding dialog.

**2. Login or Signup** — The dialog opens with the login form. Existing users can sign in with email or Google. The `user.email` prop prefills the email field.

New users click “Create account” to sign up with Google or email. When signing up with email, the `user.email` and `user.username` props are prefilled. When signing up with Google, the `user` prop values are ignored — name, email, and username are inferred from the Google account.

**3. Profile** — After signup, the user sets up their profile. The `user.name` prop prefills the name field.

**4. Connect Calendar** — The user can connect a calendar or skip this step.

**5. Authorize** — The user reviews the requested permissions and clicks “Allow”. The displayed permissions (e.g. “View event types”) correspond to the `scope` passed to the component — in this example, `["EVENT_TYPE_READ"]`.

**6. Done** — `onAuthorizationAllowed` fires with the authorization code. Exchange it for tokens using the token endpoint.

### ​Public Clients (PKCE)

Public OAuth clients cannot safely store a client secret (e.g. browser-only apps). Use PKCE to secure the authorization code exchange instead. Generate a `code_verifier`, derive a `code_challenge` from it, and pass the challenge to `OnboardingEmbed`. When you receive the authorization code, exchange it with the `code_verifier` instead of a client secret.

```
`import { OnboardingEmbed } from "@calcom/atoms";
import { useMemo, useState } from "react";

async function generatePkce() {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  const codeVerifier = btoa(String.fromCharCode(...array))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");

  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(codeVerifier));
  const codeChallenge = btoa(String.fromCharCode(...new Uint8Array(digest)))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");

  return { codeVerifier, codeChallenge };
}

export function MyApp() {
  const state = useMemo(() => crypto.randomUUID(), []);
  const [pkce, setPkce] = useState<{ codeVerifier: string; codeChallenge: string } | null>(null);

  useMemo(() => {
    generatePkce().then(setPkce);
  }, []);

  if (!pkce) return null;

  return (
    <OnboardingEmbed
      oAuthClientId="your_client_id"
      authorization={{
        scope: ["EVENT_TYPE_READ"],
        redirectUri: "https://your-app.com/cal/callback",
        state,
        codeChallenge: pkce.codeChallenge,
      }}
      onAuthorizationAllowed={async ({ code }) => {
        // Exchange using code_verifier instead of client_secret
        const res = await fetch("https://api.cal.com/v2/auth/oauth2/token", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            client_id: "your_client_id",
            code_verifier: pkce.codeVerifier,
            grant_type: "authorization_code",
            code,
            redirect_uri: "https://your-app.com/cal/callback",
          }),
        });
        const { access_token, refresh_token } = await res.json();
      }}
    />
  );
}
`
```

### ​Error Types

The `onError` callback receives an error object with the following shape:

```
`interface OnboardingError {
  code: "INVALID_PROPS" | "SIGNUP_FAILED" | "ONBOARDING_FAILED" | "AUTHORIZATION_FAILED" | "STATE_MISMATCH" | "UNKNOWN";
  message: string;
}
`
```

CodeDescription`INVALID_PROPS`Required props are missing or invalid (e.g. `oAuthClientId` does not exist, `redirectUri` does not match a registered URI, or required authorization fields are empty).`SIGNUP_FAILED`Account creation failed.`ONBOARDING_FAILED`An error occurred during the onboarding steps.`AUTHORIZATION_FAILED`The user denied access or OAuth consent failed.`STATE_MISMATCH`The `state` in the response did not match the `state` you provided. Possible CSRF attack.`UNKNOWN`An unexpected error occurred.

### ​How It Works

The component opens a dialog containing an iframe that loads Cal.com’s onboarding flow. The iframe runs on Cal.com’s domain with a first-party session, so no third-party cookies are needed.
The flow automatically detects the user’s state:

- **No session** — starts at signup/login, then profile setup, calendar connection, and OAuth consent.

- **Session with incomplete onboarding** — resumes from where the user left off.

- **Session with complete onboarding** — skips straight to OAuth consent.

After the user grants access, you receive an authorization code that you exchange for access and refresh tokens using the token endpoint.
