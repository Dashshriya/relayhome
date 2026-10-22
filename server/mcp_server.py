""""MCP tools for the RelayHome household coordination demo."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("RelayHome Care Coordination", json_response=True)

HOUSEHOLD = {
    "household_name": "The Rivera household",
    "care_recipient": "Elena Rivera",
    "coordinator": "Alex Rivera",
    "preferences": ["Confirm before assigning a person", "No medical advice", "Keep a visible activity log"],
    "demo_notice": "Synthetic demo data; no real person or appointment is represented.",
}
TASKS: list[dict] = [
    {"id": "RH-101", "title": "Confirm Thursday appointment time", "category": "Appointment", "due": "Tomorrow · 9:00 AM", "assignee": "Alex", "status": "Open", "priority": "High"},
    {"id": "RH-102", "title": "Pick up grocery order", "category": "Errands", "due": "Today · 5:30 PM", "assignee": "Jordan", "status": "In progress", "priority": "Medium"},
    {"id": "RH-103", "title": "Call Elena after lunch", "category": "Check-in", "due": "Today · 1:30 PM", "assignee": "Alex", "status": "Open", "priority": "Medium"},
]
ACTIVITY: list[dict] = [
    {"time": "10:14 AM", "event": "Household context loaded", "detail": "3 active tasks reviewed", "kind": "system"},
    {"time": "10:12 AM", "event": "Grocery pickup started", "detail": "Jordan · RH-102", "kind": "task"},
]
CHECKINS: list[dict] = []


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M UTC")


def _log(event: str, detail: str, kind: str = "task") -> None:
    ACTIVITY.insert(0, {"time": _now(), "event": event, "detail": detail, "kind": kind})


@mcp.tool()
def get_household_context() -> dict:
    """Return the synthetic household profile and coordination preferences."""
    return HOUSEHOLD


@mcp.tool()
def list_open_tasks() -> list[dict]:
    """List open and in-progress household coordination tasks."""
    return [task.copy() for task in TASKS if task["status"] != "Done"]


@mcp.tool()
def create_task(
    title: str,
    category: Literal["Appointment", "Transport", "Preparation", "Check-in", "Errands", "Other"] = "Other",
    due: str = "Tomorrow",
    assignee: str = "Unassigned",
    priority: Literal["Low", "Medium", "High"] = "Medium",
) -> dict:
    """Create a task only after the user approves a proposed plan."""
    clean_title = title.strip()
    if not clean_title or len(clean_title) > 140:
        raise ValueError("Task title must contain 1–140 characters.")
    if assignee not in {"Unassigned", "Alex", "Jordan", "Elena"}:
        raise ValueError("Choose an assignee from the available household members.")
    task = {
        "id": f"RH-{str(uuid4())[:8].upper()}", "title": clean_title,
        "category": category, "due": due[:80], "assignee": assignee,
        "status": "Open", "priority": priority,
    }
    TASKS.insert(0, task)
    _log("Task created", f"{task['title']} · {task['assignee']} · {task['id']}")
    return task


@mcp.tool()
def schedule_checkin(person: str, when: str, method: Literal["Call", "Text", "In-person"] = "Call") -> dict:
    """Add a non-medical check-in reminder to the demo state."""
    if person not in {"Elena", "Alex", "Jordan"}:
        raise ValueError("Choose a household member: Elena, Alex, or Jordan.")
    if not when.strip() or len(when) > 100:
        raise ValueError("Provide a short time description.")
    item = {"id": f"CI-{str(uuid4())[:8].upper()}", "person": person, "when": when, "method": method, "status": "Scheduled"}
    CHECKINS.insert(0, item)
    _log("Check-in scheduled", f"{method} with {person} · {when}")
    return item


@mcp.tool()
def complete_task(task_id: str) -> dict:
    """Mark a task done and record the change in the activity log."""
    for task in TASKS:
        if task["id"] == task_id:
            task["status"] = "Done"
            _log("Task completed", f"{task['title']} · {task_id}")
            return task.copy()
    raise ValueError(f"No task found with ID {task_id!r}.")


@mcp.tool()
def get_activity_log() -> list[dict]:
    """Return recent coordination events, newest first."""
    return [item.copy() for item in ACTIVITY[:30]]


@mcp.tool()
def list_checkins() -> list[dict]:
    """List scheduled non-medical check-in reminders."""
    return [item.copy() for item in CHECKINS]


if __name__ == "__main__":
    # FastMCP reads the bind address and port from its settings; run() accepts
    # the transport only. Bind locally because FastAPI proxies MCP requests.
    mcp.settings.host = "127.0.0.1"
    mcp.settings.port = 8000
    mcp.run(transport="streamable-http")
