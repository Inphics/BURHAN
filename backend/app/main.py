
import os
import hmac


from backend.app.security.agent_auth import authenticate_agent
from fastapi import FastAPI, HTTPException, Query, Header

from fastapi import FastAPI
from pydantic import BaseModel
from backend.app.execution.enforcement_engine import EnforcementEngine
from backend.app.evaluation.audit_logger import AuditLogger
from backend.app.policies.policy_engine import PolicyEngine


app = FastAPI(
    title="BURHAN API",
    description="Autonomous AI Agent Safety & Verification Framework",
    version="0.1.0",
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
        "version": "0.1.0",
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


@app.post("/enforce")
def enforce_action(
    request: ActionRequest,
    x_api_key: str | None = Header(default=None),
):
    # Identify the agent using its API key.
    agent = authenticate_agent(x_api_key)

    if agent is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing agent API key.",
        )

    # Check permissions before simulating the action.
    result = enforcement_engine.enforce(
        agent=agent,
        action=request.action,
    )

    # Record the verified agent and enforcement decision.
    audit_logger.log(
        agent=agent,
        action=request.action,
        allowed=result["allowed"],
        reason=result["reason"],
    )

    return result



