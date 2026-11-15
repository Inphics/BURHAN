
from dataclasses import dataclass
from datetime import datetime, timezone
from backend.app.evaluation.audit_database import AuditDatabase
import os
from backend.app.evaluation.audit_integrity import AuditIntegrity


@dataclass
class AuditEvent:
    timestamp: str
    agent: str
    action: str
    allowed: bool
    reason: str
    execution_status: str = "not_attempted"
    request_id: str | None = None
    event_hmac: str | None = None

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
        request_id: str | None = None,
    ):
        event = AuditEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent=agent,
            action=action,
            allowed=allowed,
            reason=reason,
            execution_status=execution_status,
            request_id=request_id,
        )

        
        secret_key = os.getenv("BURHAN_AUDIT_HMAC_KEY")
        require_signing = os.getenv("BURHAN_REQUIRE_AUDIT_SIGNING") == "true"

        if require_signing and not secret_key:
            raise RuntimeError(
                "Audit signing is required but BURHAN_AUDIT_HMAC_KEY is missing."
            )

        if secret_key:
            event_data = {
                "timestamp": event.timestamp,
                "agent": event.agent,
                "action": event.action,
                "allowed": event.allowed,
                "reason": event.reason,
                "execution_status": event.execution_status,
                "request_id": event.request_id,
            }

            event.event_hmac = AuditIntegrity.calculate_hmac(
                event_data,
                secret_key,
            )

        self.database.save_event(
            timestamp=event.timestamp,
            agent=event.agent,
            action=event.action,
            allowed=event.allowed,
            reason=event.reason,
            execution_status=event.execution_status,
            request_id=event.request_id,
            event_hmac=event.event_hmac,
        )

        self.events.append(event)
        return event

