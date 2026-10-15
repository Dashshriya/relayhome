from server.planner import propose_steps


def test_appointment_request_proposes_transport_preparation_and_checkin():
    steps = propose_steps("Mom has an appointment tomorrow. Confirm transport and pack her bag, then call to check in.")
    titles = [step.get("title", "") for step in steps]
    assert any("appointment" in title.lower() for title in titles)
    assert any("transport" in title.lower() for title in titles)
    assert any("bag" in title.lower() for title in titles)
    assert any(step["type"] == "checkin" for step in steps)


def test_grocery_request_includes_errand():
    steps = propose_steps("Please organize groceries and a check-in tomorrow")
    assert any(step.get("category") == "Errands" for step in steps)
    assert any(step["type"] == "checkin" for step in steps)


def test_unknown_request_has_safe_clarification_step():
    steps = propose_steps("Can you help with the family?")
    assert steps
    assert len(steps) <= 6
    assert all(step["type"] in {"task", "checkin"} for step in steps)
