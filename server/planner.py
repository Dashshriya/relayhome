"""A small, transparent planner for the RelayHome demo.

It uses local keyword rules rather than an LLM, so its behavior is predictable
and the demo does not need paid API credentials.
"""
from typing import Any


def propose_steps(message: str) -> list[dict[str, Any]]:
    text = message.lower()
    steps: list[dict[str, Any]] = []
    appointment = any(word in text for word in ("appointment", "doctor", "clinic", "visit"))
    travel = any(word in text for word in ("ride", "transport", "drive", "pickup", "pick up", "get there"))
    pack = any(word in text for word in ("pack", "bag", "documents", "prepare", "bring"))
    grocery = any(word in text for word in ("grocery", "groceries", "shopping", "pantry"))
    checkin = any(word in text for word in ("check in", "check-in", "call", "remind", "make sure", "follow up"))
    tomorrow = "tomorrow" in text or appointment

    if appointment:
        steps.append({"type": "task", "title": "Confirm appointment time and requirements", "category": "Appointment", "due": "Today · 6:00 PM", "assignee": "Alex", "priority": "High"})
    if travel or appointment:
        steps.append({"type": "task", "title": "Confirm transport and pickup plan", "category": "Transport", "due": "Tomorrow · 8:00 AM" if tomorrow else "Today · 6:00 PM", "assignee": "Jordan", "priority": "High"})
    if pack or appointment:
        steps.append({"type": "task", "title": "Prepare appointment bag and required documents", "category": "Preparation", "due": "Tomorrow · 7:30 AM" if tomorrow else "Today · 7:30 PM", "assignee": "Alex", "priority": "Medium"})
    if grocery:
        steps.append({"type": "task", "title": "Review grocery list and confirm pickup", "category": "Errands", "due": "Tomorrow · 5:00 PM", "assignee": "Jordan", "priority": "Medium"})
    if checkin or appointment:
        steps.append({"type": "checkin", "person": "Elena", "when": "Tomorrow · after the appointment" if tomorrow else "Today · 6:00 PM", "method": "Call"})
    if not steps:
        steps = [
            {"type": "task", "title": "Clarify the next household action", "category": "Other", "due": "Today · 6:00 PM", "assignee": "Unassigned", "priority": "Low"},
            {"type": "checkin", "person": "Elena", "when": "Tomorrow · 10:00 AM", "method": "Call"},
        ]
    return steps[:6]
