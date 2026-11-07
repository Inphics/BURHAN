
from fastapi.testclient import TestClient

from backend.app.main import app, audit_logger


def test_evaluate_endpoint_records_audit_event():
    client = TestClient(app)

    audit_logger.events.clear()

    response = client.post(
        "/evaluate",
        json={
            "agent": "research_agent",
            "action": "delete",
        },
    )

    assert response.status_code == 200
    assert response.json()["allowed"] is False

    assert len(audit_logger.events) == 1

    event = audit_logger.events[0]

    assert event.agent == "research_agent"
    assert event.action == "delete"
    assert event.allowed is False
    assert "not permitted" in event.reason
