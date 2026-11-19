
import os, hmac, sqlite3
from uuid import uuid4

from backend.app.security.agent_auth import authenticate_agent
from fastapi import FastAPI, HTTPException, Query, Header

from fastapi import FastAPI
from pydantic import BaseModel
from backend.app.execution.enforcement_engine import EnforcementEngine
from backend.app.evaluation.audit_logger import AuditLogger
from backend.app.evaluation.audit_integrity import AuditIntegrity
from backend.app.policies.policy_engine import PolicyEngine


app = FastAPI(
    title="BURHAN API",
    description="Autonomous AI Agent Safety & Verification Framework",
    version="0.2.0",
)

policy_engine = PolicyEngine()
audit_logger = AuditLogger()
enforcement_engine = EnforcementEngine(policy_engine=policy_engine)

class ActionRequest(BaseModel):
    action: str


@app.get("/")
def home():
    return {
        "project": "BURHAN",
        "version": "0.2.0",
        "status": "running",
        "description": "Autonomous AI Agent Safety & Verification Framework",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}



@app.post("/evaluate")
def evaluate_action(
    request: ActionRequest,
    x_api_key: str | None = Header(default=None),
):
    agent = authenticate_agent(x_api_key)

    if agent is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing agent API key.",
        )

    decision = policy_engine.evaluate(
        agent=agent,
        action=request.action,
    )

    audit_logger.log(
        agent=agent,
        action=request.action,
        allowed=decision.allowed,
        reason=decision.reason,
    )

    return {
        "allowed": decision.allowed,
        "reason": decision.reason,
    }



@app.get("/audit")
def get_audit_events(
    limit: int = Query(default=100, ge=1, le=100),
    x_api_key: str | None = Header(default=None),
):
    if os.getenv("BURHAN_ENABLE_AUDIT_API") != "true":
        raise HTTPException(
            status_code=403,
            detail="Audit inspection is disabled.",
        )

    expected_api_key = os.getenv("BURHAN_AUDIT_API_KEY")

    if not expected_api_key:
        raise HTTPException(
            status_code=403,
            detail="Audit API key is not configured.",
        )

    if not x_api_key or not hmac.compare_digest(
        x_api_key, expected_api_key
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key.",
        )

    events = audit_logger.database.get_events(limit=limit)

    return {
        "total_events": len(events),
        "events": events,
    }



@app.get("/audit/verify")
def verify_audit_events(
    limit: int = Query(default=100, ge=1, le=100),
    x_api_key: str | None = Header(default=None),
):
    # Require the audit API to be enabled.
    if os.getenv("BURHAN_ENABLE_AUDIT_API") != "true":
        raise HTTPException(
            status_code=403,
            detail="Audit inspection is disabled.",
        )

    # Require a configured audit API key.
    expected_api_key = os.getenv("BURHAN_AUDIT_API_KEY")

    if not expected_api_key:
        raise HTTPException(
            status_code=403,
            detail="Audit API key is not configured.",
        )

    # Authenticate the caller before accessing audit records.
    if not x_api_key or not hmac.compare_digest(
        x_api_key, expected_api_key
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key.",
        )

    # Verification requires a separate HMAC signing key.
    secret_key = os.getenv("BURHAN_AUDIT_HMAC_KEY")

    if not secret_key:
        raise HTTPException(
            status_code=503,
            detail="Audit verification key is not configured.",
        )

    # Retrieve and verify the requested audit records.
    try:
        events = audit_logger.database.get_events(limit=limit)

        return AuditIntegrity.verify_records(
            events,
            secret_key,
        )
    except (OSError, sqlite3.Error):
        raise HTTPException(
            status_code=503,
            detail="Audit verification is unavailable.",
        ) from None



@app.post("/enforce")
def enforce_action(
    request: ActionRequest,
    x_api_key: str | None = Header(default=None),
):
    # Authenticate the agent.
    agent = authenticate_agent(x_api_key)

    if agent is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing agent API key.",
        )
    request_id = str(uuid4())

    # Record the request before attempting execution.
    try:
        audit_logger.log(
            agent=agent,
            action=request.action,
            allowed=False,
            reason="Enforcement requested; decision pending.",
            execution_status="not_attempted",
            request_id=request_id,
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Audit logging is unavailable.",
        ) from None

    # Check permissions and attempt safe simulation.
    result = enforcement_engine.enforce(
        agent=agent,
        action=request.action,
    )

    if not result["allowed"]:
        execution_status = "blocked"
    elif result["executed"]:
        execution_status = "simulated"
    else:
        execution_status = "failed"

    # Record the final policy decision and outcome.
    try:
        audit_logger.log(
            agent=agent,
            action=request.action,
            allowed=result["allowed"],
            reason=result["reason"],
            execution_status=execution_status,
            request_id=request_id,
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Audit logging is unavailable.",
        ) from None

    return result
