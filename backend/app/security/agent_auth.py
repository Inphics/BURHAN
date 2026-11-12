
import hmac
import os


def authenticate_agent(api_key: str | None) -> str | None:
    """
    Identify an agent using its configured API key.

    Returns the verified agent name if the key matches.
    Returns None if authentication fails.
    """

    if not api_key:
        return None

    agent_keys = {
        "research_agent": os.getenv("BURHAN_RESEARCH_AGENT_KEY"),
        "admin_agent": os.getenv("BURHAN_ADMIN_AGENT_KEY"),
    }

    # Reject missing or duplicate configured keys.
    configured_keys = [
        key for key in agent_keys.values() if key
    ]

    if len(configured_keys) != len(set(configured_keys)):
        return None

    for agent_name, expected_key in agent_keys.items():
        if expected_key and hmac.compare_digest(
            api_key, expected_key
        ):
            return agent_name

    return None
