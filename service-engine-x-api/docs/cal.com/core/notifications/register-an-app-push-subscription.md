<!-- Source: https://cal.com/docs/api-reference/v2/notifications/register-an-app-push-subscription -->

# Register an app push subscription - Cal.com Docs

Notifications
# Register an app push subscription
Copy pageCopy pagePOST/v2/notifications/subscriptions/app-pushTry itRegister an app push subscription

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/notifications/subscriptions/app-push \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "token": "ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]",
  "platform": "IOS",
  "deviceId": "device-uuid-123"
}
'`
```
201
```
`{
  "status": "success",
  "data": {
    "id": 123,
    "userId": 123,
    "type": "<string>",
    "platform": "<string>",
    "identifier": "<string>",
    "deviceId": "<string>",
    "createdAt": "2023-11-07T05:31:56Z",
    "updatedAt": "2023-11-07T05:31:56Z"
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_
#### Body
application/json​tokenstringrequired

Expo Push TokenPattern: `EXPO_PUSH_TOKEN_REGEX`Example:

`"ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]"`​platformenum<string>required

Mobile platformAvailable options: `IOS`, `ANDROID` Example:

`"IOS"`​deviceIdstringrequired

Unique device identifierExample:

`"device-uuid-123"`
#### Response
201 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
