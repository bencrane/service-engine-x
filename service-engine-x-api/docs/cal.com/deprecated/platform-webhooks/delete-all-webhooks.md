<!-- Source: https://cal.com/docs/api-reference/v2/deprecated:-platform-webhooks/delete-all-webhooks -->

# Delete all webhooks - Cal.com Docs

Platform / Webhooks
# Delete all webhooks
Copy pageThese endpoints are deprecated and will be removed in the future.Copy pageDELETE/v2/oauth-clients/{clientId}/webhooksTry itDelete all webhooks

cURL
```
`curl --request DELETE \
  --url https://api.cal.com/v2/oauth-clients/{clientId}/webhooks \
  --header 'Authorization: Bearer <token>' \
  --header 'x-cal-secret-key: <x-cal-secret-key>'`
```
200
```
`{
  "status": "success",
  "data": "<string>"
}`
```

#### Authorizations
​Authorizationstringheaderrequired

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.
#### Headers
​x-cal-secret-keystringrequired

OAuth client secret key
#### Path Parameters
​clientIdstringrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​datastringrequired
