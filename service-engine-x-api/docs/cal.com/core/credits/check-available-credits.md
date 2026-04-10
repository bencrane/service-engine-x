<!-- Source: https://cal.com/docs/api-reference/v2/credits/check-available-credits -->

# Check available credits - Cal.com Docs

Credits
# Check available credits
Copy page

Check if the authenticated user (or their org/team) has available credits and return the current balance.Copy pageGET/v2/credits/availableTry itCheck available credits

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/credits/available \
  --header 'Authorization: Bearer <token>'`
```
200
```
`{}`
```

#### Authorizations
​Authorizationstringheaderrequired

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.
#### Response
200 - application/json

The response is of type `object`.
