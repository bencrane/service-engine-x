# cal-mcp

Remote HTTP MCP server for Cal.com, built by proxying Cal.com's official stdio MCP package.

## Architecture

`MCP Client -> auth-proxy (:8080, Bearer→X-API-Key) -> mcp-proxy (:9090, 127.0.0.1) -> @calcom/cal-mcp (stdio) -> Cal.com API v2`

## Secrets and environment

Set these in Doppler:

- `CAL_API_KEY` - Cal.com API key consumed by `@calcom/cal-mcp`
- `CAL_MCP_AUTH_TOKEN` - shared auth token required by `mcp-proxy` auth
- `PORT` - optional, defaults to `8080`

On Railway, the only platform-level env var should be `DOPPLER_TOKEN`.

## Connection

Use your Railway public URL with `/mcp`, for example:

- `https://your-service.up.railway.app/mcp`

Authenticate with either header:

- `X-API-Key: <CAL_MCP_AUTH_TOKEN>`
- `Authorization: Bearer <CAL_MCP_AUTH_TOKEN>`

Both work. A lightweight auth-proxy in front of mcp-proxy normalizes `Authorization: Bearer` → `X-API-Key` before forwarding.

## Local development

```bash
CAL_API_KEY=xxx CAL_MCP_AUTH_TOKEN=xxx ./start.sh
```
