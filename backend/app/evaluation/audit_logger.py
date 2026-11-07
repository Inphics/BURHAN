
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



class AuditLogger:
    def __init__(self, database=None):
        self.events = []
        self.database = database if database is not None else AuditDatabase()

    def log(self, agent: str, action: str, allowed: bool, reason: str):
        event = AuditEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent=agent,
            action=action,
            allowed=allowed,
            reason=reason,
        )

        self.database.save_event(
            timestamp=event.timestamp,
            agent=event.agent,
            action=event.action,
            allowed=event.allowed,
            reason=event.reason,
        )

        self.events.append(event)
        return event
