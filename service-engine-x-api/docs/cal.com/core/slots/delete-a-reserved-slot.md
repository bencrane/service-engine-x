<!-- Source: https://cal.com/docs/api-reference/v2/slots/delete-a-reserved-slot -->

# Delete a reserved slot - Cal.com Docs

Slots
# Delete a reserved slot
Copy pagePlease make sure to pass in the cal-api-version header value as mentioned in the Headers section. Not passing the correct value will default to an older version of this endpoint.Copy pageDELETE/v2/slots/reservations/{uid}Try itDelete a reserved slot

cURL
```
`curl --request DELETE \
  --url https://api.cal.com/v2/slots/reservations/{uid} \
  --header 'Authorization: Bearer <token>' \
  --header 'cal-api-version: <cal-api-version>'`
```
200
```
`{
  "status": "success"
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
200 - application/json

The response is of type `object`.
