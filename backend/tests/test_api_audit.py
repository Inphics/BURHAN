
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


def test_evaluate_endpoint_records_audit_event():
    client = TestClient(main.app)

    response = client.post(
        "/evaluate",
        json={
            "agent": "research_agent",
            "action": "delete",
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
    monkeypatch.setenv("BURHAN_ENABLE_AUDIT_API", "true")
    monkeypatch.setenv("BURHAN_AUDIT_API_KEY", "test-secret-key")

    client = TestClient(main.app)

    client.post(
        "/evaluate",
        json={
            "agent": "research_agent",
            "action": "delete",
        },
    )

    
    response = client.get(
        "/audit",
        headers={"X-API-Key": "test-secret-key"},
    )


    assert response.status_code == 200

    data = response.json()

    assert data["total_events"] == 1
    assert len(data["events"]) == 1

    event = data["events"][0]

    assert event["agent"] == "research_agent"
    assert event["action"] == "delete"
    assert event["allowed"] is False
    assert "not permitted" in event["reason"]
    assert event["timestamp"].endswith("+00:00")


def test_audit_api_accepts_valid_limit(monkeypatch):
    client = TestClient(app)

    monkeypatch.setenv("BURHAN_ENABLE_AUDIT_API", "true")
    monkeypatch.setenv("BURHAN_AUDIT_API_KEY", "test-secret-key")

    for number in range(5):
        client.post(
            "/evaluate",
            json={
                "agent": "research_agent",
                "action": "read",
            },
        )

    response = client.get(
        "/audit",
        params={"limit": 2},
        headers={"X-API-Key": "test-secret-key"},
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
