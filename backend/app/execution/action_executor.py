
class ActionExecutor:
    """
    Safely simulate agent actions.

    This executor does not perform real file operations,
    system changes, or external API calls.
    """

    SUPPORTED_ACTIONS = {"read", "report", "update", "delete"}

    def execute(self, action: str) -> dict:
        """
        Simulate an action without changing the system.
        """

        if action not in self.SUPPORTED_ACTIONS:
            return {
                "executed": False,
                "action": action,
                "message": "Unsupported action. Nothing was executed.",
            }

        return {
            "executed": True,
            "action": action,
            "message": f"Action '{action}' simulated successfully.",
        }
