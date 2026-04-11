#!/usr/bin/env bash
set -euo pipefail

: "${CAL_API_KEY:?CAL_API_KEY is required}"
: "${CAL_MCP_API_KEY:?CAL_MCP_API_KEY is required}"

export MCP_PROXY_PORT=9090

cleanup() { kill "$MCP_PID" "$PROXY_PID" 2>/dev/null; wait; }
trap cleanup EXIT

# mcp-proxy on internal-only port
npx mcp-proxy \
  --port "${MCP_PROXY_PORT}" \
  --host 127.0.0.1 \
  --apiKey "${CAL_MCP_API_KEY}" \
  -- \
  npx @calcom/cal-mcp --all-tools &
MCP_PID=$!

# auth-proxy on public port — normalizes Bearer → X-API-Key
node auth-proxy.mjs &
PROXY_PID=$!

wait -n
exit $?
