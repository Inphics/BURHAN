
from fastapi import FastAPI
from pydantic import BaseModel

from backend.app.policies.policy_engine import PolicyEngine


app = FastAPI(
    title="BURHAN API",
    description="Autonomous AI Agent Safety & Verification Framework",
    version="0.1.0",
)

policy_engine = PolicyEngine()


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

    return {
        "allowed": decision.allowed,
        "reason": decision.reason,
    }