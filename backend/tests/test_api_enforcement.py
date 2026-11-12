
import pytest
from fastapi.testclient import TestClient

from backend.app import main
from backend.app.evaluation.audit_database import AuditDatabase
from backend.app.evaluation.audit_logger import AuditLogger


@pytest.fixture(autouse=True)
def setup_enforcement_tests(monkeypatch, tmp_path):
    # Give each test its own temporary audit database.
    database = AuditDatabase(
        db_path=tmp_path / "enforcement_test.db"
    )

    monkeypatch.setattr(
        main,
        "audit_logger",
        AuditLogger(database=database),
    )

    # Configure separate API keys for both agents.
    monkeypatch.setenv(
        "BURHAN_RESEARCH_AGENT_KEY",
        "research-test-key",
    )
    monkeypatch.setenv(
        "BURHAN_ADMIN_AGENT_KEY",
        "admin-test-key",
    )


def test_enforce_rejects_missing_api_key():
    client = TestClient(main.app)

    response = client.post(
        "/enforce",
        json={"action": "read"},
    )

    assert response.status_code == 401
    assert main.audit_logger.database.get_events() == []


def test_enforce_rejects_invalid_api_key():
    client = TestClient(main.app)

    response = client.post(
        "/enforce",
        json={"action": "read"},
        headers={"X-API-Key": "wrong-key"},
    )

    assert response.status_code == 401
    assert main.audit_logger.database.get_events() == []


def test_research_agent_can_enforce_read():
    client = TestClient(main.app)

    response = client.post(
        "/enforce",
        json={"action": "read"},
        headers={"X-API-Key": "research-test-key"},
    )

    assert response.status_code == 200

    result = response.json()

    assert result["allowed"] is True
    assert result["executed"] is True
    assert result["action"] == "read"

    events = main.audit_logger.database.get_events()

    assert len(events) == 1
    assert events[0]["agent"] == "research_agent"
    assert events[0]["action"] == "read"
    assert events[0]["allowed"] is True


def test_research_agent_cannot_enforce_delete():
    client = TestClient(main.app)

    response = client.post(
        "/enforce",
        json={"action": "delete"},
        headers={"X-API-Key": "research-test-key"},
    )

    assert response.status_code == 200

    result = response.json()

    assert result["allowed"] is False
    assert result["executed"] is False

    events = main.audit_logger.database.get_events()

    assert len(events) == 1
    assert events[0]["agent"] == "research_agent"
    assert events[0]["action"] == "delete"
    assert events[0]["allowed"] is False


def test_admin_agent_can_enforce_delete():
    client = TestClient(main.app)

    response = client.post(
        "/enforce",
        json={"action": "delete"},
        headers={"X-API-Key": "admin-test-key"},
    )

    assert response.status_code == 200

    result = response.json()

    assert result["allowed"] is True
    assert result["executed"] is True

    events = main.audit_logger.database.get_events()

    assert len(events) == 1
    assert events[0]["agent"] == "admin_agent"
    assert events[0]["action"] == "delete"
    assert events[0]["allowed"] is True
