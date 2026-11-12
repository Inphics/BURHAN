
from backend.app.execution.action_executor import ActionExecutor
from backend.app.policies.policy_engine import PolicyEngine


class EnforcementEngine:
    """
    Enforce agent permissions before simulating actions.

    Denied actions never reach the executor.
    """

    def __init__(self, policy_engine=None, executor=None):
        self.policy_engine = (
            policy_engine if policy_engine is not None else PolicyEngine()
        )
        self.executor = (
            executor if executor is not None else ActionExecutor()
        )

    def enforce(self, agent: str, action: str) -> dict:
        decision = self.policy_engine.evaluate(
            agent=agent,
            action=action,
        )

        if not decision.allowed:
            return {
                "allowed": False,
                "executed": False,
                "reason": decision.reason,
                "action": action,
            }

        result = self.executor.execute(action)

        return {
            "allowed": True,
            "executed": result["executed"],
            "reason": decision.reason,
            "action": action,
            "message": result["message"],
        }
