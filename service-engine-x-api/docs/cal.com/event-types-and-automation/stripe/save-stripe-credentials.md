<!-- Source: https://cal.com/docs/api-reference/v2/stripe/save-stripe-credentials -->

# Save Stripe credentials - Cal.com Docs

Stripe
# Save Stripe credentials
Copy pageCopy pageGET/v2/stripe/saveTry itSave Stripe credentials

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/stripe/save \
  --header 'Authorization: Bearer <token>'`
```
200
```
`{
  "url": "<string>"
}`
```

#### Authorizations
​Authorizationstringheaderrequired

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.
#### Query Parameters
​statestringrequired​codestringrequired
#### Response
200 - application/json​urlstringrequired
