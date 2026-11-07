
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
