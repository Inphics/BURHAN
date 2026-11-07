
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


def test_permission_revocation():
    engine = PolicyEngine()

    before = engine.evaluate("research_agent", "read")
    assert before.allowed is True

    revoked = engine.revoke_permission("research_agent", "read")
    assert revoked is True

    after = engine.evaluate("research_agent", "read")
    assert after.allowed is False


def test_revoke_nonexistent_permission():
    engine = PolicyEngine()

    revoked = engine.revoke_permission("research_agent", "delete")

    assert revoked is False
    assert engine.evaluate("research_agent", "read").allowed is True
    assert engine.evaluate("research_agent", "report").allowed is True


def test_revoke_permission_unknown_agent():
    engine = PolicyEngine()

    revoked = engine.revoke_permission("unknown_agent", "read")

    assert revoked is False
    assert "unknown_agent" not in engine.permissions


def test_permission_granting():
    engine = PolicyEngine()

    before = engine.evaluate("research_agent", "update")
    assert before.allowed is False

    granted = engine.grant_permission("research_agent", "update")
    assert granted is True

    after = engine.evaluate("research_agent", "update")
    assert after.allowed is True


def test_grant_existing_permission():
    engine = PolicyEngine()

    granted = engine.grant_permission("research_agent", "read")

    assert granted is False
    assert engine.evaluate("research_agent", "read").allowed is True
    assert engine.permissions["research_agent"] == {"read", "report"}


def test_grant_permission_unknown_agent():
    engine = PolicyEngine()

    granted = engine.grant_permission("unknown_agent", "delete")

    assert granted is False
    assert "unknown_agent" not in engine.permissions
    assert engine.evaluate("unknown_agent", "delete").allowed is False


def test_full_permission_lifecycle():
    engine = PolicyEngine()

    # Initially, the agent cannot update
    assert engine.evaluate("research_agent", "update").allowed is False

    # Grant the permission
    assert engine.grant_permission("research_agent", "update") is True

    # The agent can now update
    assert engine.evaluate("research_agent", "update").allowed is True

    # Revoke the permission
    assert engine.revoke_permission("research_agent", "update") is True

    # The agent can no longer update
    assert engine.evaluate("research_agent", "update").allowed is False
