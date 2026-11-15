
from backend.app.execution.action_executor import ActionExecutor
from backend.app.policies.policy_engine import PolicyEngine


class EnforcementEngine:
    """
    Enforce agent permissions before simulating actions.

    Denied actions never reach the executor.
    Executor failures are handled without reporting
    successful execution.
    """

    def __init__(self, policy_engine=None, executor=None):
        self.policy_engine = (
            policy_engine if policy_engine is not None else PolicyEngine()
        )
        self.executor = (
            executor if executor is not None else ActionExecutor()
        )

    def enforce(self, agent: str, action: str) -> dict:
        # Step 1: Check the agent's permissions.
        decision = self.policy_engine.evaluate(
            agent=agent,
            action=action,
        )

        # Step 2: Block denied actions before execution.
        if not decision.allowed:
            return {
                "allowed": False,
                "executed": False,
                "reason": decision.reason,
                "action": action,
            }

        # Step 3: Safely attempt the simulated action.
        try:
            result = self.executor.execute(action)
        except Exception:
            return {
                "allowed": True,
                "executed": False,
                "reason": decision.reason,
                "action": action,
                "error": "Action execution failed.",
            }

        # Step 4: Return the execution result.
        return {
            "allowed": True,
            "executed": result["executed"],
            "reason": decision.reason,
            "action": action,
            "message": result["message"],
        }
