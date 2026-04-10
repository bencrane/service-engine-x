# cal-mcp

Remote HTTP MCP server for Cal.com, built by proxying Cal.com's official stdio MCP package.

## Architecture

`MCP Client -> mcp-proxy (HTTP) -> @calcom/cal-mcp (stdio) -> Cal.com API v2`

## Secrets and environment

Set these in Doppler:

- `CAL_API_KEY` - Cal.com API key consumed by `@calcom/cal-mcp`
- `CAL_MCP_API_KEY` - shared API key required by `mcp-proxy` auth
- `PORT` - optional, defaults to `8080`

On Railway, the only platform-level env var should be `DOPPLER_TOKEN`.

## Connection

Use your Railway public URL with `/mcp`, for example:

- `https://your-service.up.railway.app/mcp`

Authenticate with:

- `X-API-Key: <CAL_MCP_API_KEY>`

`Authorization: Bearer <CAL_MCP_API_KEY>` may work depending on your client/proxy chain, but `X-API-Key` is the canonical header for this setup.

## Local development

```bash
CAL_API_KEY=xxx CAL_MCP_API_KEY=xxx npx mcp-proxy --port 8080 --apiKey "$CAL_MCP_API_KEY" -- npx @calcom/cal-mcp --all-tools
```
