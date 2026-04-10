<!-- Source: https://cal.com/docs/api-reference/v2/orgs-users/delete-a-user -->

# Delete a user - Cal.com Docs

Users
# Delete a user
Copy page

Required membership role: `org admin`. PBAC permission: `organization.remove`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageDELETE/v2/organizations/{orgId}/users/{userId}Try itDelete a user

cURL
```
`curl --request DELETE \
  --url https://api.cal.com/v2/organizations/{orgId}/users/{userId}`
```
200
```
`{
  "status": "success",
  "data": {
    "id": 1,
    "email": "[email protected]",
    "timeZone": "America/New_York",
    "weekStart": "Monday",
    "hideBranding": false,
    "createdDate": "2022-01-01T00:00:00Z",
    "profile": {
      "id": 1,
      "organizationId": 1,
      "userId": 1,
      "username": "john_doe"
    },
    "username": "john_doe",
    "name": "John Doe",
    "emailVerified": "2022-01-01T00:00:00Z",
    "bio": "I am a software developer",
    "avatarUrl": "https://example.com/avatar.jpg",
    "appTheme": "light",
    "theme": "default",
    "defaultScheduleId": 1,
    "locale": "en-US",
    "timeFormat": 12,
    "brandColor": "#ffffff",
    "darkBrandColor": "#000000",
    "allowDynamicBooking": true,
    "verified": true,
    "invitedTo": 1,
    "metadata": {
      "key": "value"
    }
  }
}`
```

#### Headers
​Authorizationstring

For non-platform customers - value must be `Bearer <token>` where `<token>` is api key prefixed with cal_​x-cal-secret-keystring

For platform customers - OAuth client secret key​x-cal-client-idstring

For platform customers - OAuth client ID
#### Path Parameters
​orgIdnumberrequired​userIdnumberrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
