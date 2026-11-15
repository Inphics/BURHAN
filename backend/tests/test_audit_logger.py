
from datetime import datetime

from backend.app.evaluation.audit_database import AuditDatabase
from backend.app.evaluation.audit_logger import AuditLogger


def test_audit_logger_records_event(tmp_path):
    test_database = AuditDatabase(tmp_path / "test_audit.db")
    logger = AuditLogger(database=test_database)

    event = logger.log(
        agent="research_agent",
        action="delete",
        allowed=False,
        reason="Permission denied",
    )

    assert len(logger.events) == 1
    assert logger.events[0] == event

    assert event.agent == "research_agent"
    assert event.action == "delete"
    assert event.allowed is False
    assert event.reason == "Permission denied"

    timestamp = datetime.fromisoformat(event.timestamp)
    assert timestamp.utcoffset().total_seconds() == 0

    saved_events = test_database.get_events()

    assert len(saved_events) == 1
    assert saved_events[0]["agent"] == "research_agent"
    assert saved_events[0]["action"] == "delete"
    assert saved_events[0]["allowed"] is False


def test_audit_events_survive_database_reconnection(tmp_path):
    database_path = tmp_path / "persistent_audit.db"

    first_database = AuditDatabase(database_path)
    first_logger = AuditLogger(database=first_database)

    first_logger.log(
        agent="research_agent",
        action="delete",
        allowed=False,
        reason="Permission denied",
    )

    second_database = AuditDatabase(database_path)
    saved_events = second_database.get_events()

    assert len(saved_events) == 1
    assert saved_events[0]["agent"] == "research_agent"
    assert saved_events[0]["action"] == "delete"
    assert saved_events[0]["allowed"] is False
    assert saved_events[0]["reason"] == "Permission denied"


def test_audit_database_uses_environment_variable(tmp_path, monkeypatch):
    custom_database_path = tmp_path / "custom_audit.db"

    monkeypatch.setenv(
        "BURHAN_AUDIT_DB_PATH",
        str(custom_database_path),
    )

    database = AuditDatabase()

    assert database.db_path == custom_database_path
    assert custom_database_path.exists()


def test_audit_database_respects_event_limit(tmp_path):
    database = AuditDatabase(tmp_path / "limited_audit.db")

    for number in range(5):
        database.save_event(
            timestamp=f"2026-01-01T00:00:0{number}+00:00",
            agent="research_agent",
            action="read",
            allowed=True,
            reason=f"Test event {number}",
        )

    events = database.get_events(limit=2)

    assert len(events) == 2
    assert events[0]["reason"] == "Test event 4"
    assert events[1]["reason"] == "Test event 3"


def test_audit_logger_saves_valid_hmac(tmp_path, monkeypatch):
    from backend.app.evaluation.audit_database import AuditDatabase
    from backend.app.evaluation.audit_integrity import AuditIntegrity
    from backend.app.evaluation.audit_logger import AuditLogger

    secret = "test-only-hmac-secret"
    monkeypatch.setenv("BURHAN_AUDIT_HMAC_KEY", secret)

    database = AuditDatabase(tmp_path / "signed_audit.db")
    logger = AuditLogger(database=database)

    event = logger.log(
        agent="research_agent",
        action="read",
        allowed=True,
        reason="Action permitted.",
        execution_status="simulated",
        request_id="test-request-123",
    )

    records = database.get_events()

    assert len(records) == 1

    stored_record = records[0]

    # Confirm that SQLite contains the generated signature.
    assert stored_record["event_hmac"] is not None
    assert stored_record["event_hmac"] == event.event_hmac

    # Reconstruct exactly the fields that were signed.
    signed_data = {
        "timestamp": stored_record["timestamp"],
        "agent": stored_record["agent"],
        "action": stored_record["action"],
        "allowed": stored_record["allowed"],
        "reason": stored_record["reason"],
        "execution_status": stored_record["execution_status"],
        "request_id": stored_record["request_id"],
    }

    # Verify the stored record using the secret.
    assert AuditIntegrity.verify_hmac(
        signed_data,
        secret,
        stored_record["event_hmac"],
    ) is True

    # Simulate a modified audit record.
    signed_data["action"] = "delete"

    assert AuditIntegrity.verify_hmac(
        signed_data,
        secret,
        stored_record["event_hmac"],
    ) is False



def test_sqlite_audit_tampering_invalidates_hmac(tmp_path, monkeypatch):
    import sqlite3

    from backend.app.evaluation.audit_database import AuditDatabase
    from backend.app.evaluation.audit_integrity import AuditIntegrity
    from backend.app.evaluation.audit_logger import AuditLogger

    secret = "test-only-hmac-secret"
    monkeypatch.setenv("BURHAN_AUDIT_HMAC_KEY", secret)

    database = AuditDatabase(tmp_path / "tampering_test.db")
    logger = AuditLogger(database=database)

    logger.log(
        agent="research_agent",
        action="read",
        allowed=True,
        reason="Action permitted.",
        execution_status="simulated",
        request_id="tampering-test-123",
    )

    # Directly modify the SQLite record without updating its HMAC.
    with sqlite3.connect(database.db_path) as connection:
        connection.execute(
            """
            UPDATE audit_events
            SET action = ?
            WHERE id = ?
            """,
            ("delete", 1),
        )

    records = database.get_events()
    assert len(records) == 1

    tampered_record = records[0]

    signed_data = {
        "timestamp": tampered_record["timestamp"],
        "agent": tampered_record["agent"],
        "action": tampered_record["action"],
        "allowed": tampered_record["allowed"],
        "reason": tampered_record["reason"],
        "execution_status": tampered_record["execution_status"],
        "request_id": tampered_record["request_id"],
    }

    assert tampered_record["action"] == "delete"
    assert tampered_record["event_hmac"] is not None

    # The stored signature must not match the modified record.
    assert AuditIntegrity.verify_hmac(
        signed_data,
        secret,
        tampered_record["event_hmac"],
    ) is False


def test_verify_records_classifies_sqlite_events(tmp_path, monkeypatch):
    import sqlite3

    from backend.app.evaluation.audit_database import AuditDatabase
    from backend.app.evaluation.audit_integrity import AuditIntegrity
    from backend.app.evaluation.audit_logger import AuditLogger

    secret = "test-only-hmac-secret"
    monkeypatch.setenv("BURHAN_AUDIT_HMAC_KEY", secret)

    database = AuditDatabase(tmp_path / "verification_test.db")
    logger = AuditLogger(database=database)

    # Create two signed records.
    logger.log(
        agent="research_agent",
        action="read",
        allowed=True,
        reason="Action permitted.",
        execution_status="simulated",
        request_id="request-one",
    )

    logger.log(
        agent="research_agent",
        action="report",
        allowed=True,
        reason="Action permitted.",
        execution_status="simulated",
        request_id="request-two",
    )

    # Modify the second record directly in SQLite.
    with sqlite3.connect(database.db_path) as connection:
        connection.execute(
            "UPDATE audit_events SET action = ? WHERE id = ?",
            ("delete", 2),
        )

        # Insert an unsigned historical-style record.
        connection.execute(
            """
            INSERT INTO audit_events (
                timestamp,
                agent,
                action,
                allowed,
                reason,
                execution_status,
                request_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "2026-11-15T12:00:00+00:00",
                "research_agent",
                "read",
                1,
                "Historical record.",
                "not_attempted",
                None,
            ),
        )

    records = database.get_events()
    result = AuditIntegrity.verify_records(records, secret)

    assert result["total"] == 3
    assert result["valid"] == 1
    assert result["invalid"] == 1
    assert result["unsigned"] == 1

    statuses = {
        item["id"]: item["status"]
        for item in result["results"]
    }

    assert statuses[1] == "valid"
    assert statuses[2] == "invalid"
    assert statuses[3] == "unsigned"


def test_strict_audit_signing_rejects_missing_key(tmp_path, monkeypatch):
    import pytest

    from backend.app.evaluation.audit_database import AuditDatabase
    from backend.app.evaluation.audit_logger import AuditLogger

    monkeypatch.setenv("BURHAN_REQUIRE_AUDIT_SIGNING", "true")
    monkeypatch.delenv("BURHAN_AUDIT_HMAC_KEY", raising=False)

    database = AuditDatabase(tmp_path / "strict_signing_test.db")
    logger = AuditLogger(database=database)

    with pytest.raises(
        RuntimeError,
        match="Audit signing is required",
    ):
        logger.log(
            agent="research_agent",
            action="read",
            allowed=True,
            reason="Action permitted.",
            execution_status="simulated",
            request_id="strict-test-123",
        )

    # Failed signing must not create an unsigned audit record.
    assert database.get_events() == []
