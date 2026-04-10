<!-- Source: https://cal.com/docs/api-reference/v2/notifications/remove-an-app-push-subscription -->

# Remove an app push subscription - Cal.com Docs

Notifications
# Remove an app push subscription
Copy pageCopy pageDELETE/v2/notifications/subscriptions/app-pushTry itRemove an app push subscription

cURL
```
`curl --request DELETE \
  --url https://api.cal.com/v2/notifications/subscriptions/app-push \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "token": "ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]"
}
'`
```
200
```
`{
  "status": "success",
  "message": "App push subscription removed successfully"
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_
#### Body
application/json​tokenstringrequired

Expo Push Token to removePattern: `EXPO_PUSH_TOKEN_REGEX`Example:

`"ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]"`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​messagestringrequiredExample:

`"App push subscription removed successfully"`
