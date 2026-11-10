
import os

from fastapi import FastAPI, HTTPException, Query

from fastapi import FastAPI
from pydantic import BaseModel

from backend.app.evaluation.audit_logger import AuditLogger
from backend.app.policies.policy_engine import PolicyEngine


app = FastAPI(
    title="BURHAN API",
    description="Autonomous AI Agent Safety & Verification Framework",
    version="0.1.0",
)

policy_engine = PolicyEngine()
audit_logger = AuditLogger()


class ActionRequest(BaseModel):
    agent: str
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
def evaluate_action(request: ActionRequest):
    decision = policy_engine.evaluate(
        agent=request.agent,
        action=request.action,
    )

    audit_logger.log(
        agent=request.agent,
        action=request.action,
        allowed=decision.allowed,
        reason=decision.reason,
    )

    return {
        "allowed": decision.allowed,
        "reason": decision.reason,
    }



@app.get("/audit")
def get_audit_events(limit: int = Query(default=100, ge=1, le=100)):
    if os.getenv("BURHAN_ENABLE_AUDIT_API") != "true":
        raise HTTPException(
            status_code=403,
            detail="Audit inspection is disabled.",
        )

    events = audit_logger.database.get_events(limit=limit)

    return {
        "total_events": len(events),
        "events": events,
    }


