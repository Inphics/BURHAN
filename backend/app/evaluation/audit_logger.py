
from dataclasses import dataclass
from datetime import datetime, timezone

from backend.app.evaluation.audit_database import AuditDatabase


@dataclass
class AuditEvent:
    timestamp: str
    agent: str
    action: str
    allowed: bool
    reason: str
    execution_status: str = "not_attempted"


class AuditLogger:
    def __init__(self, database=None):
        self.events = []
        self.database = (
            database if database is not None else AuditDatabase()
        )

    def log(
        self,
        agent: str,
        action: str,
        allowed: bool,
        reason: str,
        execution_status: str = "not_attempted",
    ):
        event = AuditEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent=agent,
            action=action,
            allowed=allowed,
            reason=reason,
            execution_status=execution_status,
        )

        self.database.save_event(
            timestamp=event.timestamp,
            agent=event.agent,
            action=event.action,
            allowed=event.allowed,
            reason=event.reason,
            execution_status=event.execution_status,
        )

        self.events.append(event)

        return event
