
from dataclasses import dataclass


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str


class PolicyEngine:
    def __init__(self):
        self.permissions = {
            "research_agent": {"read", "report"},
            "admin_agent": {"read", "report", "update", "delete"},
        }

    
    def grant_permission(self, agent: str, action: str) -> bool:
        allowed_actions = self.permissions.get(agent)

        if allowed_actions is None or action in allowed_actions:
            return False

        allowed_actions.add(action)
        return True

    def revoke_permission(self, agent: str, action: str) -> bool:
        allowed_actions = self.permissions.get(agent)

        if allowed_actions is None or action not in allowed_actions:
            return False

        allowed_actions.remove(action)
        return True

    def evaluate(self, agent: str, action: str) -> PolicyDecision:
        allowed_actions = self.permissions.get(agent, set())

        if action in allowed_actions:
            return PolicyDecision(
                allowed=True,
                reason=f"Agent '{agent}' is permitted to perform '{action}'.",
            )

        return PolicyDecision(
            allowed=False,
            reason=f"Agent '{agent}' is not permitted to perform '{action}'.",
        )