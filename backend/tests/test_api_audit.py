
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
    assert events[0]["execution_status"] == "not_attempted"


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


def test_audit_verify_rejects_missing_api_key(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.app.main import app

    monkeypatch.setenv("BURHAN_ENABLE_AUDIT_API", "true")
    monkeypatch.setenv("BURHAN_AUDIT_API_KEY", "test-only-audit-key")
    monkeypatch.setenv("BURHAN_AUDIT_HMAC_KEY", "test-only-hmac-key")

    client = TestClient(app)

    response = client.get("/audit/verify")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key."


def test_audit_verify_rejects_incorrect_api_key(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.app.main import app

    monkeypatch.setenv("BURHAN_ENABLE_AUDIT_API", "true")
    monkeypatch.setenv("BURHAN_AUDIT_API_KEY", "correct-test-audit-key")
    monkeypatch.setenv("BURHAN_AUDIT_HMAC_KEY", "test-only-hmac-key")

    client = TestClient(app)

    response = client.get(
        "/audit/verify",
        headers={
            "X-API-Key": "incorrect-test-audit-key",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key."


def test_audit_verify_rejects_when_disabled(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.app.main import app

    # Disable audit API access.
    monkeypatch.setenv("BURHAN_ENABLE_AUDIT_API", "false")

    # Configure test-only keys.
    monkeypatch.setenv(
        "BURHAN_AUDIT_API_KEY",
        "test-only-audit-key",
    )
    monkeypatch.setenv(
        "BURHAN_AUDIT_HMAC_KEY",
        "test-only-hmac-key",
    )

    client = TestClient(app)

    response = client.get(
        "/audit/verify",
        headers={
            "X-API-Key": "test-only-audit-key",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Audit inspection is disabled."


def test_audit_verify_rejects_missing_hmac_key(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.app.main import app

    monkeypatch.setenv("BURHAN_ENABLE_AUDIT_API", "true")
    monkeypatch.setenv("BURHAN_AUDIT_API_KEY", "test-only-audit-key")

    # Remove the HMAC key for this test.
    monkeypatch.delenv("BURHAN_AUDIT_HMAC_KEY", raising=False)

    client = TestClient(app)

    response = client.get(
        "/audit/verify",
        headers={
            "X-API-Key": "test-only-audit-key",
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Audit verification key is not configured."
    )


def test_audit_verify_accepts_valid_signed_record(
    tmp_path, monkeypatch
):
    from fastapi.testclient import TestClient

    from backend.app import main
    from backend.app.evaluation.audit_database import AuditDatabase
    from backend.app.evaluation.audit_logger import AuditLogger

    audit_api_key = "test-only-audit-api-key"
    hmac_key = "test-only-hmac-secret"

    monkeypatch.setenv("BURHAN_ENABLE_AUDIT_API", "true")
    monkeypatch.setenv("BURHAN_AUDIT_API_KEY", audit_api_key)
    monkeypatch.setenv("BURHAN_AUDIT_HMAC_KEY", hmac_key)

    # Use a temporary database, not the real audit database.
    database = AuditDatabase(tmp_path / "verification_api_test.db")
    logger = AuditLogger(database=database)

    # Replace the API's logger for this test only.
    monkeypatch.setattr(main, "audit_logger", logger)

    # Create an authentic signed audit event.
    logger.log(
        agent="research_agent",
        action="read",
        allowed=True,
        reason="Action permitted.",
        execution_status="simulated",
        request_id="verification-request-123",
    )

    client = TestClient(main.app)

    response = client.get(
        "/audit/verify",
        headers={"X-API-Key": audit_api_key},
    )

    assert response.status_code == 200

    result = response.json()

    assert result["total"] == 1
    assert result["valid"] == 1
    assert result["invalid"] == 0
    assert result["unsigned"] == 0

    assert len(result["results"]) == 1
    assert result["results"][0]["status"] == "valid"
    assert (
        result["results"][0]["request_id"]
        == "verification-request-123"
    )


def test_audit_verify_detects_tampered_sqlite_record(
    tmp_path, monkeypatch
):
    import sqlite3

    from fastapi.testclient import TestClient

    from backend.app import main
    from backend.app.evaluation.audit_database import AuditDatabase
    from backend.app.evaluation.audit_logger import AuditLogger

    audit_api_key = "test-only-audit-api-key"
    hmac_key = "test-only-hmac-secret"

    monkeypatch.setenv("BURHAN_ENABLE_AUDIT_API", "true")
    monkeypatch.setenv("BURHAN_AUDIT_API_KEY", audit_api_key)
    monkeypatch.setenv("BURHAN_AUDIT_HMAC_KEY", hmac_key)

    database = AuditDatabase(tmp_path / "tampered_api_test.db")
    logger = AuditLogger(database=database)

    # Use the temporary audit database for this test.
    monkeypatch.setattr(main, "audit_logger", logger)

    # Create a correctly signed audit record.
    logger.log(
        agent="research_agent",
        action="read",
        allowed=True,
        reason="Action permitted.",
        execution_status="simulated",
        request_id="tampered-request-123",
    )

    # Simulate tampering directly in SQLite.
    with sqlite3.connect(database.db_path) as connection:
        connection.execute(
            """
            UPDATE audit_events
            SET action = ?
            WHERE request_id = ?
            """,
            ("delete", "tampered-request-123"),
        )

    client = TestClient(main.app)

    response = client.get(
        "/audit/verify",
        headers={"X-API-Key": audit_api_key},
    )

    assert response.status_code == 200

    result = response.json()

    assert result["total"] == 1
    assert result["valid"] == 0
    assert result["invalid"] == 1
    assert result["unsigned"] == 0

    assert len(result["results"]) == 1
    assert result["results"][0]["status"] == "invalid"
    assert (
        result["results"][0]["request_id"]
        == "tampered-request-123"
    )


def test_audit_verify_identifies_unsigned_record(
    tmp_path, monkeypatch
):
    from fastapi.testclient import TestClient

    from backend.app import main
    from backend.app.evaluation.audit_database import AuditDatabase

    audit_api_key = "test-only-audit-api-key"

    monkeypatch.setenv("BURHAN_ENABLE_AUDIT_API", "true")
    monkeypatch.setenv("BURHAN_AUDIT_API_KEY", audit_api_key)
    monkeypatch.setenv(
        "BURHAN_AUDIT_HMAC_KEY",
        "test-only-hmac-secret",
    )

    database = AuditDatabase(tmp_path / "unsigned_api_test.db")

    # Save an unsigned record, as older audit versions did.
    database.save_event(
        timestamp="2026-11-15T12:00:00+00:00",
        agent="research_agent",
        action="read",
        allowed=True,
        reason="Historical record.",
        execution_status="not_attempted",
        request_id="historical-request-123",
    )

    # Make the API read from our temporary database.
    monkeypatch.setattr(
        main.audit_logger,
        "database",
        database,
    )

    client = TestClient(main.app)

    response = client.get(
        "/audit/verify",
        headers={"X-API-Key": audit_api_key},
    )

    assert response.status_code == 200

    result = response.json()

    assert result["total"] == 1
    assert result["valid"] == 0
    assert result["invalid"] == 0
    assert result["unsigned"] == 1

    assert result["results"][0]["status"] == "unsigned"
    assert (
        result["results"][0]["request_id"]
        == "historical-request-123"
    )


def test_audit_verify_respects_record_limit(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    from backend.app import main
    from backend.app.evaluation.audit_database import AuditDatabase
    from backend.app.evaluation.audit_logger import AuditLogger

    audit_api_key = "test-only-audit-api-key"

    monkeypatch.setenv("BURHAN_ENABLE_AUDIT_API", "true")
    monkeypatch.setenv("BURHAN_AUDIT_API_KEY", audit_api_key)
    monkeypatch.setenv(
        "BURHAN_AUDIT_HMAC_KEY",
        "test-only-hmac-secret",
    )

    database = AuditDatabase(tmp_path / "limit_test.db")
    logger = AuditLogger(database=database)

    monkeypatch.setattr(main, "audit_logger", logger)

    # Create three signed audit records.
    for index in range(3):
        logger.log(
            agent="research_agent",
            action="read",
            allowed=True,
            reason="Action permitted.",
            execution_status="simulated",
            request_id=f"request-{index}",
        )

    client = TestClient(main.app)

    response = client.get(
        "/audit/verify?limit=2",
        headers={"X-API-Key": audit_api_key},
    )

    assert response.status_code == 200

    result = response.json()

    assert result["total"] == 2
    assert result["valid"] == 2
    assert result["invalid"] == 0
    assert result["unsigned"] == 0
    assert len(result["results"]) == 2
