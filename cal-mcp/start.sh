#!/usr/bin/env bash
set -euo pipefail

: "${CAL_API_KEY:?CAL_API_KEY is required}"
: "${CAL_MCP_API_KEY:?CAL_MCP_API_KEY is required}"

exec npx mcp-proxy \
  --port "${PORT:-8080}" \
  --apiKey "${CAL_MCP_API_KEY}" \
  -- \
  npx @calcom/cal-mcp --all-tools
