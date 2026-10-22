#!/usr/bin/env bash
set -euo pipefail

python -m server.mcp_server &
MCP_PID=$!

cleanup() {
  kill "$MCP_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Wait briefly for the local MCP Streamable HTTP server to bind its port.
for attempt in $(seq 1 30); do
  if python -c 'import socket; s=socket.socket(); s.settimeout(0.25); s.connect(("127.0.0.1", 8000)); s.close()' 2>/dev/null; then
    break
  fi
  sleep 1
done

uvicorn server.api:app --host 0.0.0.0 --port "${PORT:-10000}"
