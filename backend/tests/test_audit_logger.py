
from datetime import datetime

from backend.app.evaluation.audit_logger import AuditLogger


def test_audit_logger_records_event():
    logger = AuditLogger()

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
