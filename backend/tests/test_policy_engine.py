
from backend.app.policies.policy_engine import PolicyEngine


def test_research_agent_can_read():
    engine = PolicyEngine()

    decision = engine.evaluate("research_agent", "read")

    assert decision.allowed is True


def test_research_agent_cannot_delete():
    engine = PolicyEngine()

    decision = engine.evaluate("research_agent", "delete")

    assert decision.allowed is False


def test_admin_agent_can_delete():
    engine = PolicyEngine()

    decision = engine.evaluate("admin_agent", "delete")

    assert decision.allowed is True


def test_unknown_agent_is_denied():
    engine = PolicyEngine()

    decision = engine.evaluate("unknown_agent", "read")

    assert decision.allowed is False


def test_unknown_action_is_denied():
    engine = PolicyEngine()

    decision = engine.evaluate("admin_agent", "transfer_money")

    assert decision.allowed is False