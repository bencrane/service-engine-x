<!-- Source: https://cal.com/docs/api-reference/v2/credits/charge-credits -->

# Charge credits - Cal.com Docs

Credits
# Charge credits
Copy page

Charge credits for a completed AI agent interaction. Uses externalRef for idempotency to prevent double-charging.Copy pagePOST/v2/credits/chargeTry itCharge credits

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/credits/charge \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "credits": 5,
  "creditFor": "AI_AGENT",
  "externalRef": "agent-thread-123-1711432800000"
}
'`
```
200
```
`{}`
```

#### Authorizations
​Authorizationstringheaderrequired

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.
#### Body
application/json​creditsnumberrequired

Number of credits to chargeRequired range: `x >= 1`Example:

`5`​creditForenum<string>required

What the credits are being charged forAvailable options: `SMS`, `CAL_AI_PHONE_CALL`, `AI_AGENT` Example:

`"AI_AGENT"`​externalRefstring

Unique external reference for idempotencyExample:

`"agent-thread-123-1711432800000"`
#### Response
200 - application/json

The response is of type `object`.
