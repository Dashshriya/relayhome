# RelayHome — Devpost Submission Pack

## Title
RelayHome — Care, Coordinated

## Tagline
A human-approved household care coordinator that turns everyday requests into reviewable tasks through a self-hosted MCP server using Streamable HTTP.

## Primary track
Alexa+ — simulated web experience using a self-hosted MCP server. Do not claim a physical Alexa+ device or partner-console connection.

## Project description
Family care depends on small acts of coordination: confirming an appointment, preparing what someone needs, arranging transport, and remembering to check in. When these actions are scattered across notes and conversations, the coordination burden often falls on one person.

RelayHome gives a household one calm place to turn a request into a short plan, review the proposed tasks, and record what was actually accepted. A user describes a coordination need in plain language. RelayHome proposes a bounded set of steps with task titles, categories, timing, and suggested assignees. Nothing is saved until a person reviews and approves the plan. Approved tasks and check-in reminders are created through named MCP tools, and changes appear in a visible activity trail.

The live MCP tools panel discovers the tools advertised by the running server over Streamable HTTP, making the protocol integration inspectable in the demo. The prototype uses fictional household records and a transparent local rule-based planner. It does not send messages, alter real calendars, or offer medical advice.

## Implementation
- React + Vite dashboard
- FastAPI + Pydantic API
- MCP Python SDK with a self-hosted server and Streamable HTTP client/server communication
- Deterministic local planner
- pytest API and planner tests

Architecture: React dashboard → FastAPI API → MCP client session → self-hosted MCP server → fictional household demo state.

## What changed during the submission window
This branch adds a live MCP tool-discovery endpoint (`GET /api/mcp/tools`) that initializes a Streamable HTTP session and returns the server's live `tools/list` metadata. The dashboard displays connection state and discovered tool descriptions, and a regression test covers the endpoint. Verify these changes locally before claiming the feature works in the demo.

## Product feedback draft — verify after running the app
**MCP Python SDK / Streamable HTTP:** Used for tool declarations, session initialization, tool discovery, and actions. Named tools provide a clean boundary between the UI and actions. More prominent setup diagnostics and a single-command launcher would make first-run testing easier. Would use it again for MCP prototypes; a real-device or partner-console test is still needed before claiming real Alexa+ deployment.

**FastAPI / Pydantic:** Used for route handling and request validation. The API is straightforward to test separately. The local demo currently requires multiple services to be started, so a one-command launcher would reduce setup friction. Would use again for a small testable API layer.

**React / Vite:** Used for the dashboard, plan-review flow, MCP inspector, and activity trail. They support fast UI iteration; live protocol state depends on the API and MCP server running. Would use again for a web-based simulator.

Edit this feedback to reflect your real onboarding and test experience before submitting.

## Optional friction log draft — only submit if accurate
- **Task:** Determine how to validate a self-hosted MCP server against a real Alexa+ device or console.
- **Steps:** Review the Alexa+ requirements and published FAQ for a participant-accessible connection route.
- **Expected:** A documented way for hackathon participants to connect the server to a real Alexa+ endpoint.
- **Observed:** The published FAQ says the real device/console path is not generally available to participants; the supported alternative is a web simulation using MCP over Streamable HTTP.
- **Severity:** Medium — prevents real-device end-to-end testing but not simulated protocol testing.
- **Workaround:** Show actual MCP session/tool discovery and approved tool calls through the web simulation.
- **Suggestion:** Provide a sandboxed Alexa+ test endpoint or temporary partner-preview access for hackathon participants.

## Mini-challenge entry: Open Source

- **Mini-challenge:** Open Source
- **Contribution URL:** https://github.com/Dashshriya/crisismesh/tree/opensource-mcp-streamable-http-smokecheck/mcp-streamable-http-smokecheck
- **Pull request:** https://github.com/Dashshriya/crisismesh/pull/2
- **Repository URL:** https://github.com/Dashshriya/crisismesh
- **GitHub username:** Dashshriya
- **Description:** Added a separate MIT-licensed command-line utility that initializes an MCP Streamable HTTP session, lists the tools advertised by a server, prints tool schemas, and can optionally call a discovered tool. It reports connection failures with a non-zero exit code. The utility is separate from RelayHome, which is the primary Alexa+ track submission.

The branch/PR URLs are live but the contribution is not merged. Verify the folder is public and the code can be run before submitting these details.

## Before submission
- Run `python -m pytest -q` and `npm run build` for RelayHome.
- Start the MCP server, FastAPI, and Vite frontend; confirm the MCP panel says Connected and lists live tools.
- Draft a plan, inspect it, approve it, then show the updated task and activity list.
- Verify the separate smokecheck utility against a test MCP server.
- Record a public English video under 3 minutes.
- Do not claim AWS Builder eligibility unless a qualifying AWS service/tool was actually integrated and documented.
