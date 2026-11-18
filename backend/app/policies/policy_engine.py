
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str


class PolicyEngine:
    def __init__(self):
        config_path = (
            Path(__file__).resolve().parents[2]
            / "config"
            / "policies.json"
        )

        with config_path.open("r", encoding="utf-8") as file:
            config = json.load(file)

        if not isinstance(config, dict):
            raise ValueError("Policy configuration must be a JSON object.")

        unexpected_fields = set(config) - {"permissions"}

        if unexpected_fields:
            raise ValueError(
                "Unknown policy configuration fields: "
                + ", ".join(sorted(unexpected_fields))
            )

        raw_permissions = config.get("permissions")

        if not isinstance(raw_permissions, dict):
            raise ValueError(
                "Policy configuration must contain a permissions object."
            )

        self.permissions = {}

        for agent, actions in raw_permissions.items():
            if not isinstance(agent, str) or not agent:
                raise ValueError("Policy agent names must be non-empty strings.")

            if not isinstance(actions, list):
                raise ValueError(
                    f"Permissions for '{agent}' must be a list."
                )

            if not all(
                isinstance(action, str) and action
                for action in actions
            ):
                raise ValueError(
                    f"Permissions for '{agent}' must contain only "
                    "non-empty action strings."
                )

            self.permissions[agent] = set(actions)

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
