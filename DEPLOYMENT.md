# Deploy RelayHome

This repository includes a single-container deployment for the dashboard, FastAPI application, and local MCP Streamable HTTP server.

## Deploy to Render

1. Sign in to [Render](https://render.com/) and connect the GitHub account that owns this repository.
2. Choose **New → Blueprint** and select this repository.
3. Select branch `amazon-hackathon/relayhome-mcp-inspector`. Render reads `render.yaml` and builds the Docker image.
4. Wait for the first deployment to finish. Render assigns a public HTTPS URL.
5. Open the URL and verify the dashboard loads.
6. Open `/api/health` on the same hostname and confirm the response reports `"status":"ok"` and `"mcp":"connected"`.
7. In the dashboard, verify MCP tool discovery, draft a plan, approve it, and confirm the task and activity log update.

## Architecture

- React/Vite frontend is built into `dist/` in the Docker image.
- FastAPI serves the frontend and the `/api/*` endpoints from the same public origin.
- The startup script launches the MCP server on loopback port 8000 and then starts Uvicorn on Render's `PORT`.
- The demo uses synthetic household data and in-memory state. Restarting the service resets demo changes; do not enter real personal or medical information.

## Local production check

```bash
docker build -t relayhome .
docker run --rm -p 10000:10000 relayhome
```

Then open `http://localhost:10000`. Use `http://localhost:10000/api/health` to check backend connectivity.
