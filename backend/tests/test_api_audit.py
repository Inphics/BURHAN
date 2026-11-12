
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

from backend.app import main
from backend.app.evaluation.audit_database import AuditDatabase
from backend.app.evaluation.audit_logger import AuditLogger


@pytest.fixture(autouse=True)
def isolated_audit_database(tmp_path, monkeypatch):
    test_logger = AuditLogger(
        database=AuditDatabase(tmp_path / "test_audit.db")
    )

    monkeypatch.setattr(main, "audit_logger", test_logger)



def test_evaluate_endpoint_records_audit_event(monkeypatch):
    client = TestClient(main.app)

    monkeypatch.setenv(
        "BURHAN_RESEARCH_AGENT_KEY",
        "research-test-key",
    )

    response = client.post(
        "/evaluate",
        json={
            "action": "delete",
        },
        headers={
            "X-API-Key": "research-test-key",
        },
    )

    assert response.status_code == 200
    assert response.json()["allowed"] is False

    events = main.audit_logger.database.get_events()

    assert len(events) == 1

    event = events[0]

    assert event["agent"] == "research_agent"
    assert event["action"] == "delete"
    assert event["allowed"] is False
    assert "not permitted" in event["reason"]



def test_audit_endpoint_disabled_by_default(monkeypatch):
    monkeypatch.delenv("BURHAN_ENABLE_AUDIT_API", raising=False)

    client = TestClient(main.app)

    response = client.get("/audit")

    assert response.status_code == 403
    assert response.json()["detail"] == "Audit inspection is disabled."



def test_audit_endpoint_returns_recorded_events(monkeypatch):
    client = TestClient(main.app)

    # Configure the research agent's API key
    monkeypatch.setenv(
        "BURHAN_RESEARCH_AGENT_KEY",
        "research-test-key",
    )

    # Enable audit inspection and configure its API key
    monkeypatch.setenv(
        "BURHAN_ENABLE_AUDIT_API",
        "true",
    )
    monkeypatch.setenv(
        "BURHAN_AUDIT_API_KEY",
        "test-secret-key",
    )

    # Authenticate the research agent and record an action
    response = client.post(
        "/evaluate",
        json={
            "action": "read",
        },
        headers={
            "X-API-Key": "research-test-key",
        },
    )

    assert response.status_code == 200
    assert response.json()["allowed"] is True

    # Retrieve the recorded event using the audit API key
    response = client.get(
        "/audit",
        headers={
            "X-API-Key": "test-secret-key",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_events"] == 1
    assert len(data["events"]) == 1

    event = data["events"][0]

    assert event["agent"] == "research_agent"
    assert event["action"] == "read"
    assert event["allowed"] is True




def test_audit_api_accepts_valid_limit(monkeypatch):
    client = TestClient(main.app)

    monkeypatch.setenv(
        "BURHAN_RESEARCH_AGENT_KEY",
        "research-test-key",
    )
    monkeypatch.setenv(
        "BURHAN_ENABLE_AUDIT_API",
        "true",
    )
    monkeypatch.setenv(
        "BURHAN_AUDIT_API_KEY",
        "test-secret-key",
    )

    for number in range(5):
        response = client.post(
            "/evaluate",
            json={
                "action": "read",
            },
            headers={
                "X-API-Key": "research-test-key",
            },
        )
        assert response.status_code == 200

    response = client.get(
        "/audit",
        params={"limit": 2},
        headers={
            "X-API-Key": "test-secret-key",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_events"] == 2
    assert len(data["events"]) == 2



def test_audit_api_rejects_invalid_limits(monkeypatch):
    client = TestClient(app)
    monkeypatch.setenv("BURHAN_ENABLE_AUDIT_API", "true")
    monkeypatch.setenv("BURHAN_AUDIT_API_KEY", "test-secret-key")

    for invalid_limit in [0, -1, 101, 500]:
        response = client.get(
            "/audit",
            params={"limit": invalid_limit},
            headers={"X-API-Key": "test-secret-key"},
        )

        assert response.status_code == 422


def test_audit_api_requires_valid_api_key(monkeypatch):
    client = TestClient(app)

    monkeypatch.setenv("BURHAN_ENABLE_AUDIT_API", "true")
    monkeypatch.setenv(
        "BURHAN_AUDIT_API_KEY",
        "test-secret-key",
    )

    # Request without an API key
    response = client.get("/audit")
    assert response.status_code == 401

    # Request with an incorrect API key
    response = client.get(
        "/audit",
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 401

    # Request with the correct API key
    response = client.get(
        "/audit",
        headers={"X-API-Key": "test-secret-key"},
    )
    assert response.status_code == 200


def test_audit_api_disabled_even_with_valid_key(monkeypatch):
    client = TestClient(app)

    monkeypatch.delenv(
        "BURHAN_ENABLE_AUDIT_API",
        raising=False,
    )
    monkeypatch.setenv(
        "BURHAN_AUDIT_API_KEY",
        "test-secret-key",
    )

    response = client.get(
        "/audit",
        headers={"X-API-Key": "test-secret-key"},
    )

    assert response.status_code == 403


def test_evaluate_rejects_invalid_agent_keys(monkeypatch):
    client = TestClient(main.app)

    monkeypatch.setenv(
        "BURHAN_RESEARCH_AGENT_KEY",
        "research-test-key",
    )
    monkeypatch.setenv(
        "BURHAN_ADMIN_AGENT_KEY",
        "admin-test-key",
    )

    # Missing API key
    response = client.post(
        "/evaluate",
        json={"action": "read"},
    )
    assert response.status_code == 401

    # Incorrect API key
    response = client.post(
        "/evaluate",
        json={"action": "read"},
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 401

    # Correct research agent key
    response = client.post(
        "/evaluate",
        json={"action": "read"},
        headers={"X-API-Key": "research-test-key"},
    )
    assert response.status_code == 200
    assert response.json()["allowed"] is True


def test_admin_agent_can_request_delete(monkeypatch):
    client = TestClient(main.app)

    monkeypatch.setenv(
        "BURHAN_RESEARCH_AGENT_KEY",
        "research-test-key",
    )
    monkeypatch.setenv(
        "BURHAN_ADMIN_AGENT_KEY",
        "admin-test-key",
    )

    response = client.post(
        "/evaluate",
        json={
            "action": "delete",
        },
        headers={
            "X-API-Key": "admin-test-key",
        },
    )

    assert response.status_code == 200
    assert response.json()["allowed"] is True

    events = main.audit_logger.database.get_events()

    assert len(events) == 1

    event = events[0]

    assert event["agent"] == "admin_agent"
    assert event["action"] == "delete"
    assert event["allowed"] is True
