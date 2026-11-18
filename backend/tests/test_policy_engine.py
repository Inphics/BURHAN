
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


def test_policy_engine_rejects_invalid_permissions(tmp_path, monkeypatch):
    import json
    import pytest

    from backend.app.policies import policy_engine

    invalid_config = {
        "permissions": {
            "research_agent": "read"
        }
    }

    config_directory = tmp_path / "config"
    config_directory.mkdir()

    config_file = config_directory / "policies.json"
    config_file.write_text(
        json.dumps(invalid_config),
        encoding="utf-8",
    )

    original_path = policy_engine.Path

    def redirected_path(*args, **kwargs):
        if args and args[0] == policy_engine.__file__:
            return original_path(
                tmp_path / "app" / "policies" / "policy_engine.py"
            )
        return original_path(*args, **kwargs)

    monkeypatch.setattr(policy_engine, "Path", redirected_path)

    with pytest.raises(ValueError, match="must be a list"):
        policy_engine.PolicyEngine()


def test_unknown_agent_is_denied_with_json_policy():
    from backend.app.policies.policy_engine import PolicyEngine

    engine = PolicyEngine()

    decision = engine.evaluate(
        agent="unknown_agent",
        action="read",
    )

    assert decision.allowed is False
    assert "not permitted" in decision.reason


def test_policy_engine_rejects_missing_configuration(tmp_path, monkeypatch):
    import pytest

    from backend.app.policies import policy_engine

    original_path = policy_engine.Path

    def redirected_path(*args, **kwargs):
        if args and args[0] == policy_engine.__file__:
            return original_path(
                tmp_path / "app" / "policies" / "policy_engine.py"
            )
        return original_path(*args, **kwargs)

    monkeypatch.setattr(policy_engine, "Path", redirected_path)

    # No config/policies.json file exists in this temporary directory.
    with pytest.raises(FileNotFoundError):
        policy_engine.PolicyEngine()


def test_policy_engine_rejects_unknown_configuration_fields(
    tmp_path, monkeypatch
):
    import json
    import pytest

    from backend.app.policies import policy_engine

    invalid_config = {
        "permissions": {
            "research_agent": ["read", "report"]
        },
        "allow_everything": True,
    }

    config_directory = tmp_path / "config"
    config_directory.mkdir()

    config_file = config_directory / "policies.json"
    config_file.write_text(
        json.dumps(invalid_config),
        encoding="utf-8",
    )

    original_path = policy_engine.Path

    def redirected_path(*args, **kwargs):
        if args and args[0] == policy_engine.__file__:
            return original_path(
                tmp_path / "app" / "policies" / "policy_engine.py"
            )
        return original_path(*args, **kwargs)

    monkeypatch.setattr(policy_engine, "Path", redirected_path)

    with pytest.raises(
        ValueError,
        match="Unknown policy configuration fields",
    ):
        policy_engine.PolicyEngine()


def test_policy_engine_rejects_empty_agent_name(tmp_path, monkeypatch):
    import json
    import pytest

    from backend.app.policies import policy_engine

    config_directory = tmp_path / "config"
    config_directory.mkdir()

    config_file = config_directory / "policies.json"
    config_file.write_text(
        json.dumps({
            "permissions": {
                "": ["read"]
            }
        }),
        encoding="utf-8",
    )

    original_path = policy_engine.Path

    def redirected_path(*args, **kwargs):
        if args and args[0] == policy_engine.__file__:
            return original_path(
                tmp_path / "app" / "policies" / "policy_engine.py"
            )
        return original_path(*args, **kwargs)

    monkeypatch.setattr(policy_engine, "Path", redirected_path)

    with pytest.raises(ValueError, match="agent names"):
        policy_engine.PolicyEngine()


def test_policy_engine_rejects_empty_action_name(tmp_path, monkeypatch):
    import json
    import pytest

    from backend.app.policies import policy_engine

    config_directory = tmp_path / "config"
    config_directory.mkdir()

    config_file = config_directory / "policies.json"
    config_file.write_text(
        json.dumps({
            "permissions": {
                "research_agent": ["read", ""]
            }
        }),
        encoding="utf-8",
    )

    original_path = policy_engine.Path

    def redirected_path(*args, **kwargs):
        if args and args[0] == policy_engine.__file__:
            return original_path(
                tmp_path / "app" / "policies" / "policy_engine.py"
            )
        return original_path(*args, **kwargs)

    monkeypatch.setattr(policy_engine, "Path", redirected_path)

    with pytest.raises(ValueError, match="non-empty action strings"):
        policy_engine.PolicyEngine()


def test_policy_engine_enforces_json_permissions():
    from backend.app.policies.policy_engine import PolicyEngine

    engine = PolicyEngine()

    # Research agent can read and report.
    assert engine.evaluate("research_agent", "read").allowed is True
    assert engine.evaluate("research_agent", "report").allowed is True

    # Research agent cannot update or delete.
    assert engine.evaluate("research_agent", "update").allowed is False
    assert engine.evaluate("research_agent", "delete").allowed is False

    # Admin agent has all four configured permissions.
    assert engine.evaluate("admin_agent", "read").allowed is True
    assert engine.evaluate("admin_agent", "report").allowed is True
    assert engine.evaluate("admin_agent", "update").allowed is True
    assert engine.evaluate("admin_agent", "delete").allowed is True
