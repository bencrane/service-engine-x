<!-- Source: https://cal.com/docs/api-reference/v2/stripe/get-stripe-connect-url -->

# Get Stripe connect URL - Cal.com Docs

Stripe
# Get Stripe connect URL
Copy pageCopy pageGET/v2/stripe/connectTry itGet Stripe connect URL

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/stripe/connect \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success",
  "data": {
    "authUrl": "<string>"
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
