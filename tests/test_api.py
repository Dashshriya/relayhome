"""API route tests with MCP calls replaced by deterministic demo responses."""
from fastapi.testclient import TestClient

from server import api


client = TestClient(api.app)


def test_health_reports_connected_when_mcp_responds(monkeypatch):
    async def fake_call(name, arguments=None):
        assert name == "get_household_context"
        return {"household_name": "Test household"}

    monkeypatch.setattr(api, "call_mcp_tool", fake_call)
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "mcp": "connected",
        "household": "Test household",
    }


def test_plan_returns_reviewable_steps_without_saving(monkeypatch):
    calls = []

    async def fake_call(name, arguments=None):
        calls.append((name, arguments))
        return {"household_name": "Test household", "care_recipient": "Sam"}

    monkeypatch.setattr(api, "call_mcp_tool", fake_call)
    response = client.post(
        "/api/plan",
        json={"message": "Appointment tomorrow, confirm transport and call to check in"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["steps"]
    assert payload["planner"] == "transparent-local-rules"
    assert "Review them" in payload["summary"]
    assert [name for name, _ in calls] == ["get_household_context"]


def test_execute_records_each_approved_step_through_mcp(monkeypatch):
    calls = []

    async def fake_call(name, arguments=None):
        calls.append((name, arguments))
        return {"ok": True, "tool": name}

    monkeypatch.setattr(api, "call_mcp_tool", fake_call)
    response = client.post(
        "/api/execute",
        json={
            "steps": [
                {
                    "type": "task",
                    "title": "Confirm ride",
                    "category": "Transport",
                    "due": "Tomorrow",
                    "assignee": "Jordan",
                    "priority": "High",
                },
                {"type": "checkin", "person": "Elena", "when": "Tomorrow", "method": "Call"},
            ]
        },
    )

    assert response.status_code == 200
    assert response.json()["executed"] == 2
    assert [name for name, _ in calls] == ["create_task", "schedule_checkin"]
    assert calls[0][1]["title"] == "Confirm ride"
    assert calls[1][1]["person"] == "Elena"


def test_execute_rejects_unsupported_step_type():
    response = client.post("/api/execute", json={"steps": [{"type": "message"}]})

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported plan step type."


def test_plan_rejects_too_short_request():
    response = client.post("/api/plan", json={"message": "hi"})

    assert response.status_code == 422



def test_mcp_tool_discovery_returns_live_tool_metadata(monkeypatch):
    async def fake_discover():
        return [{
            "name": "list_open_tasks",
            "description": "List open and in-progress household coordination tasks.",
            "input_schema": {"type": "object", "properties": {}},
        }]

    monkeypatch.setattr(api, "discover_mcp_tools", fake_discover)
    response = client.get("/api/mcp/tools")

    assert response.status_code == 200
    payload = response.json()
    assert payload["transport"] == "Streamable HTTP"
    assert payload["server"] == "RelayHome Care Coordination"
    assert payload["tools"][0]["name"] == "list_open_tasks"
