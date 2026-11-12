
from backend.app.security.agent_auth import authenticate_agent


def test_valid_research_agent_key(monkeypatch):
    monkeypatch.setenv("BURHAN_RESEARCH_AGENT_KEY", "research-test-key")
    monkeypatch.setenv("BURHAN_ADMIN_AGENT_KEY", "admin-test-key")

    agent = authenticate_agent("research-test-key")

    assert agent == "research_agent"


def test_valid_admin_agent_key(monkeypatch):
    monkeypatch.setenv("BURHAN_RESEARCH_AGENT_KEY", "research-test-key")
    monkeypatch.setenv("BURHAN_ADMIN_AGENT_KEY", "admin-test-key")

    agent = authenticate_agent("admin-test-key")

    assert agent == "admin_agent"


def test_invalid_agent_key(monkeypatch):
    monkeypatch.setenv("BURHAN_RESEARCH_AGENT_KEY", "research-test-key")
    monkeypatch.setenv("BURHAN_ADMIN_AGENT_KEY", "admin-test-key")

    agent = authenticate_agent("wrong-key")

    assert agent is None


def test_missing_agent_key(monkeypatch):
    monkeypatch.setenv("BURHAN_RESEARCH_AGENT_KEY", "research-test-key")
    monkeypatch.setenv("BURHAN_ADMIN_AGENT_KEY", "admin-test-key")

    agent = authenticate_agent(None)

    assert agent is None


def test_duplicate_agent_keys_are_rejected(monkeypatch):
    monkeypatch.setenv("BURHAN_RESEARCH_AGENT_KEY", "same-key")
    monkeypatch.setenv("BURHAN_ADMIN_AGENT_KEY", "same-key")

    agent = authenticate_agent("same-key")

    assert agent is None
