# RelayHome

RelayHome helps families keep everyday care tasks from slipping through the cracks. It turns a request into a short plan, lets someone review it, and records what was actually added to the shared task list.

This is an early hackathon prototype. It uses fictional household data and a small rule-based planner; it does not send messages, create calendar events, or give medical advice.

## What you can try

- Describe a coordination need, such as preparing for an appointment.
- Review the suggested tasks and check-in before approving them.
- See saved tasks and recent activity in the dashboard.
- Open **MCP tools** to discover the tools actually advertised by the running Streamable HTTP server.
- Mark a task complete and see the activity trail update.

## How it is built

- React and Vite for the dashboard
- FastAPI for the application API
- Model Context Protocol (MCP) over Streamable HTTP for tool calls
- A deterministic Python planner, so the demo runs without paid model credentials

```text
React dashboard → FastAPI API → MCP client → MCP server → demo household state
```

## Run locally

Requirements: Python 3.11+, Node.js 20+, and npm.

Install Python dependencies:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Start each service in a separate terminal from the repository root:

```bash
python server/mcp_server.py
```

```bash
uvicorn server.api:app --host 127.0.0.1 --port 8001 --reload
```

```bash
npm install
npm run dev
```

Open the local URL printed by Vite, normally http://127.0.0.1:5173.

## Checks

```bash
python -m pytest -q
npm run build
```

For an end-to-end check, start the MCP server, the FastAPI service, and Vite in separate terminals. Confirm that the MCP tools panel changes to **Connected**, shows the tools returned by `tools/list`, and that drafting, approving, and completing a task update the activity log.

## Scope and safety

- All people and household records are fictional.
- No real notifications, messages, or calendar changes are made.
- Suggested actions require a person to review and approve them.
- RelayHome is a coordination aid, not a medical or emergency service.

## Hackathon notes

The project targets the Alexa+ track as a developer-built MCP/web prototype. It is not connected to an Alexa+ device or a partner-only console; the demo uses the simulated-experience path. The dashboard's MCP panel discovers the running server's tools over Streamable HTTP and reports connection failures without pretending the server is online.

### Submission-window update

This branch adds a live MCP tool-discovery endpoint (`GET /api/mcp/tools`), a dashboard inspector for the server's `tools/list` response, and a regression test for the endpoint. Keep the Devpost demo focused on this working integration and the human approval step before tasks are saved.
