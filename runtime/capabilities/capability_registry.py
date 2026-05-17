"""Registry for agent capability profiles."""

from typing import Any


class CapabilityRegistry:
    """Stores and retrieves capability lists per agent ID."""

    def __init__(self) -> None:

        self.agent_capabilities: dict[str, list[Any]] = {}

    def register(self, agent_id: str, capabilities: list[Any]) -> None:

        self.agent_capabilities[agent_id] = capabilities

    def get(self, agent_id: str) -> list[Any]:

        return self.agent_capabilities.get(agent_id, [])
