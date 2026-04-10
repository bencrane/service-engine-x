<!-- Source: https://cal.com/docs/api-reference/v2/slots/get-reserved-slot -->

# Get reserved slot - Cal.com Docs

Slots
# Get reserved slot
Copy pagePlease make sure to pass in the cal-api-version header value as mentioned in the Headers section. Not passing the correct value will default to an older version of this endpoint.Copy pageGET/v2/slots/reservations/{uid}Try itGet reserved slot

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/slots/reservations/{uid} \
  --header 'Authorization: Bearer <token>' \
  --header 'cal-api-version: <cal-api-version>'`
```
200
```
`{
  "status": "success",
  "data": null
}`
```

#### Authorizations
​Authorizationstringheaderrequired

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.
#### Headers
​cal-api-versionstringdefault:2024-09-04required

Must be set to 2024-09-04. If not set to this value, the endpoint will default to an older version.
#### Path Parameters
​uidstringrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataunknownrequired
