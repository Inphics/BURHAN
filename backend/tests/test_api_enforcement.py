
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

    # The database returns newest events first.
    assert len(events) == 2

    # Final execution outcome.
    assert events[0]["agent"] == "research_agent"
    assert events[0]["action"] == "read"
    assert events[0]["allowed"] is True
    assert events[0]["execution_status"] == "simulated"

    # Pre-execution audit record.
    assert events[1]["agent"] == "research_agent"
    assert events[1]["action"] == "read"
    assert events[1]["allowed"] is False
    assert events[1]["execution_status"] == "not_attempted"
    assert events[1]["reason"] == (
        "Enforcement requested; decision pending."
    )


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

    # Two audit records: final outcome and initial request.
    assert len(events) == 2

    # Final outcome: action was blocked.
    assert events[0]["agent"] == "research_agent"
    assert events[0]["action"] == "delete"
    assert events[0]["allowed"] is False
    assert events[0]["execution_status"] == "blocked"

    # Initial audit record: execution not yet attempted.
    assert events[1]["agent"] == "research_agent"
    assert events[1]["action"] == "delete"
    assert events[1]["allowed"] is False
    assert events[1]["execution_status"] == "not_attempted"
    assert events[1]["reason"] == (
        "Enforcement requested; decision pending."
    )


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

    # Two records: final outcome and pre-execution request.
    assert len(events) == 2

    # Final outcome: administrator action was simulated.
    assert events[0]["agent"] == "admin_agent"
    assert events[0]["action"] == "delete"
    assert events[0]["allowed"] is True
    assert events[0]["execution_status"] == "simulated"

    # Initial record: execution had not yet been attempted.
    assert events[1]["agent"] == "admin_agent"
    assert events[1]["action"] == "delete"
    assert events[1]["allowed"] is False
    assert events[1]["execution_status"] == "not_attempted"
    assert events[1]["reason"] == (
        "Enforcement requested; decision pending."
    )


from unittest.mock import Mock


def test_failed_execution_is_reported_safely(monkeypatch):
    client = TestClient(main.app)

    # Simulate an executor crash.
    failing_executor = Mock()
    failing_executor.execute.side_effect = RuntimeError(
        "Internal executor failure"
    )

    monkeypatch.setattr(
        main.enforcement_engine,
        "executor",
        failing_executor,
    )

    response = client.post(
        "/enforce",
        json={"action": "delete"},
        headers={"X-API-Key": "admin-test-key"},
    )

    assert response.status_code == 200

    result = response.json()

    assert result["allowed"] is True
    assert result["executed"] is False
    assert result["error"] == "Action execution failed."

    
    events = main.audit_logger.database.get_events()

    # Two audit records should exist.
    assert len(events) == 2

    # Final outcome: execution failed.
    assert events[0]["agent"] == "admin_agent"
    assert events[0]["action"] == "delete"
    assert events[0]["allowed"] is True
    assert events[0]["execution_status"] == "failed"

    # Initial record: execution had not been attempted.
    assert events[1]["agent"] == "admin_agent"
    assert events[1]["action"] == "delete"
    assert events[1]["allowed"] is False
    assert events[1]["execution_status"] == "not_attempted"
    assert events[1]["reason"] == (
        "Enforcement requested; decision pending."
    )

    # Verify that the executor was called exactly once.
    failing_executor.execute.assert_called_once_with("delete")



def test_enforce_does_not_report_success_when_audit_fails(monkeypatch):
    client = TestClient(main.app)

    # Simulate an audit database failure.
    failing_log = Mock(
        side_effect=RuntimeError("Database unavailable")
    )

    monkeypatch.setattr(
        main.audit_logger,
        "log",
        failing_log,
    )

    response = client.post(
        "/enforce",
        json={"action": "read"},
        headers={"X-API-Key": "research-test-key"},
    )

    # The API must not return a successful response
    # when the required audit record cannot be saved.
    assert response.status_code == 503

    assert response.json()["detail"] == (
        "Audit logging is unavailable."
    )


def test_audit_failure_prevents_executor_call(monkeypatch):
    client = TestClient(main.app)

    # Replace the executor with a mock so we can
    # verify whether execution was attempted.
    executor = Mock()

    monkeypatch.setattr(
        main.enforcement_engine,
        "executor",
        executor,
    )

    # Simulate audit logging being unavailable.
    monkeypatch.setattr(
        main.audit_logger,
        "log",
        Mock(side_effect=RuntimeError("Database unavailable")),
    )

    response = client.post(
        "/enforce",
        json={"action": "read"},
        headers={"X-API-Key": "research-test-key"},
    )

    assert response.status_code == 503

    # An audit failure must prevent execution.
    executor.execute.assert_not_called()


def test_enforce_audit_records_share_request_id():
    client = TestClient(main.app)

    response = client.post(
        "/enforce",
        json={"action": "read"},
        headers={"X-API-Key": "research-test-key"},
    )

    assert response.status_code == 200

    events = main.audit_logger.database.get_events()

    assert len(events) == 2

    # Both audit records must have a request ID.
    assert events[0]["request_id"] is not None
    assert events[1]["request_id"] is not None

    # The two records must belong to the same enforcement request.
    assert events[0]["request_id"] == events[1]["request_id"]

    # The records represent different stages of enforcement.
    assert events[0]["execution_status"] == "simulated"
    assert events[1]["execution_status"] == "not_attempted"


def test_separate_enforcement_requests_have_different_ids():
    client = TestClient(main.app)

    first_response = client.post(
        "/enforce",
        json={"action": "read"},
        headers={"X-API-Key": "research-test-key"},
    )

    second_response = client.post(
        "/enforce",
        json={"action": "report"},
        headers={"X-API-Key": "research-test-key"},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    events = main.audit_logger.database.get_events()

    # Each enforcement request produces two audit records.
    assert len(events) == 4

    # Records are returned newest first.
    second_request_final = events[0]
    second_request_initial = events[1]
    first_request_final = events[2]
    first_request_initial = events[3]

    # Each pair must share one request ID.
    assert (
        first_request_final["request_id"]
        == first_request_initial["request_id"]
    )

    assert (
        second_request_final["request_id"]
        == second_request_initial["request_id"]
    )

    # Separate enforcement requests must have different IDs.
    assert (
        first_request_final["request_id"]
        != second_request_final["request_id"]
    )
