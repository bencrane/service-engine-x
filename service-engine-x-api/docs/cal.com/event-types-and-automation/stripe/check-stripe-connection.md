<!-- Source: https://cal.com/docs/api-reference/v2/stripe/check-stripe-connection -->

# Check Stripe connection - Cal.com Docs

Stripe
# Check Stripe connection
Copy pageCopy pageGET/v2/stripe/checkTry itCheck Stripe connection

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/stripe/check \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success"
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`
