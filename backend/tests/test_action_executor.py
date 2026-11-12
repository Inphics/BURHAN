
import pytest

from backend.app.execution.action_executor import ActionExecutor


@pytest.mark.parametrize(
    "action",
    ["read", "report", "update", "delete"],
)
def test_supported_actions_are_simulated(action):
    executor = ActionExecutor()

    result = executor.execute(action)

    assert result["executed"] is True
    assert result["action"] == action
    assert result["message"] == (
        f"Action '{action}' simulated successfully."
    )


def test_unsupported_action_is_rejected():
    executor = ActionExecutor()

    result = executor.execute("unknown")

    assert result["executed"] is False
    assert result["action"] == "unknown"
    assert result["message"] == (
        "Unsupported action. Nothing was executed."
    )
