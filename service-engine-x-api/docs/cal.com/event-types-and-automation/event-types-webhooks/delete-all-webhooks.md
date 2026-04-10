<!-- Source: https://cal.com/docs/api-reference/v2/event-types-webhooks/delete-all-webhooks -->

# Delete all webhooks - Cal.com Docs

Webhooks
# Delete all webhooks
Copy pageCopy pageDELETE/v2/event-types/{eventTypeId}/webhooksTry itDelete all webhooks

cURL
```
`curl --request DELETE \
  --url https://api.cal.com/v2/event-types/{eventTypeId}/webhooks \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success",
  "data": "<string>"
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​eventTypeIdnumberrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​datastringrequired
