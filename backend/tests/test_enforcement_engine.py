
from unittest.mock import Mock

from backend.app.execution.enforcement_engine import EnforcementEngine


def test_research_agent_can_execute_read():
    engine = EnforcementEngine()

    result = engine.enforce(
        agent="research_agent",
        action="read",
    )

    assert result["allowed"] is True
    assert result["executed"] is True
    assert result["action"] == "read"


def test_research_agent_cannot_execute_delete():
    executor = Mock()

    engine = EnforcementEngine(executor=executor)

    result = engine.enforce(
        agent="research_agent",
        action="delete",
    )

    assert result["allowed"] is False
    assert result["executed"] is False

    # The executor must never be called for denied actions.
    executor.execute.assert_not_called()


def test_admin_agent_can_execute_delete():
    engine = EnforcementEngine()

    result = engine.enforce(
        agent="admin_agent",
        action="delete",
    )

    assert result["allowed"] is True
    assert result["executed"] is True


def test_unknown_agent_cannot_execute_action():
    executor = Mock()

    engine = EnforcementEngine(executor=executor)

    result = engine.enforce(
        agent="unknown_agent",
        action="read",
    )

    assert result["allowed"] is False
    assert result["executed"] is False

    executor.execute.assert_not_called()
