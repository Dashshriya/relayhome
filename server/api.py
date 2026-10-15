"""FastAPI routes used by the RelayHome dashboard."""
from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from server.planner import propose_steps

MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp")
app = FastAPI(title="RelayHome API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


class PlanRequest(BaseModel):
    message: str = Field(min_length=3, max_length=600)


class ExecuteRequest(BaseModel):
    steps: list[dict[str, Any]] = Field(min_length=1, max_length=8)


async def call_mcp_tool(name: str, arguments: dict[str, Any] | None = None) -> Any:
    """Initialize an MCP session and call one tool on the local server."""
    try:
        async with streamablehttp_client(MCP_URL) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments or {})
                if result.isError:
                    raise RuntimeError("MCP tool returned an error")
                parsed = []
                for item in result.content:
                    if getattr(item, "text", None):
                        try:
                            parsed.append(json.loads(item.text))
                        except json.JSONDecodeError:
                            parsed.append(item.text)
                if len(parsed) == 1:
                    return parsed[0]
                return parsed
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"MCP server unavailable or tool failed: {exc}") from exc


@app.get("/api/health")
async def health() -> dict:
    try:
        context = await call_mcp_tool("get_household_context")
        return {"status": "ok", "mcp": "connected", "household": context.get("household_name", "demo")}
    except HTTPException:
        return {"status": "degraded", "mcp": "unavailable"}


@app.get("/api/overview")
async def overview() -> dict:
    context, tasks, activity, checkins = await asyncio.gather(
        call_mcp_tool("get_household_context"),
        call_mcp_tool("list_open_tasks"),
        call_mcp_tool("get_activity_log"),
        call_mcp_tool("list_checkins"),
    )
    return {"context": context, "tasks": tasks, "activity": activity, "checkins": checkins}


@app.post("/api/plan")
async def plan(request: PlanRequest) -> dict:
    steps = propose_steps(request.message)
    context = await call_mcp_tool("get_household_context")
    return {
        "plan_id": "draft-" + str(abs(hash(request.message)))[:8],
        "summary": f"I drafted {len(steps)} coordination steps for {context.get('care_recipient', 'your household')}. Review them before anything is saved.",
        "steps": steps,
        "safety_note": "Nothing has changed yet. Review assignments and times before approving.",
        "planner": "transparent-local-rules",
    }


@app.post("/api/execute")
async def execute(request: ExecuteRequest) -> dict:
    results = []
    for step in request.steps:
        if step.get("type") == "task":
            result = await call_mcp_tool("create_task", {
                "title": str(step.get("title", "")),
                "category": step.get("category", "Other"),
                "due": str(step.get("due", "Tomorrow")),
                "assignee": step.get("assignee", "Unassigned"),
                "priority": step.get("priority", "Medium"),
            })
        elif step.get("type") == "checkin":
            result = await call_mcp_tool("schedule_checkin", {
                "person": step.get("person", "Elena"),
                "when": str(step.get("when", "Tomorrow")),
                "method": step.get("method", "Call"),
            })
        else:
            raise HTTPException(status_code=400, detail="Unsupported plan step type.")
        results.append(result)
    return {"executed": len(results), "results": results, "message": "Approved steps were recorded through MCP tools."}


@app.post("/api/complete/{task_id}")
async def complete(task_id: str) -> dict:
    return await call_mcp_tool("complete_task", {"task_id": task_id})
