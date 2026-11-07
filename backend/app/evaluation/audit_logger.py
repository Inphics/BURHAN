
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class AuditEvent:
    timestamp: str
    agent: str
    action: str
    allowed: bool
    reason: str


class AuditLogger:
    def __init__(self):
        self.events = []

    def log(self, agent: str, action: str, allowed: bool, reason: str):
        event = AuditEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent=agent,
            action=action,
            allowed=allowed,
            reason=reason,
        )

        self.events.append(event)
        return event
