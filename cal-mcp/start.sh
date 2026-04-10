#!/usr/bin/env bash
set -euo pipefail

exec npx mcp-proxy \
  --port "${PORT:-8080}" \
  --apiKey "${CAL_MCP_API_KEY}" \
  -- \
  npx @calcom/cal-mcp --all-tools
