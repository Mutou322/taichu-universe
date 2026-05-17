"""Agent registry for storing and looking up agent instances."""

from typing import Any


class AgentRegistry:
    """Registry that stores agents by ID with register/unregister/get operations."""

    def __init__(self) -> None:
        self.agents: dict[str, Any] = {}

    def register(self, agent: Any) -> None:
        self.agents[agent.agent_id] = agent

    def unregister(self, agent_id: str) -> None:
        if agent_id in self.agents:
            del self.agents[agent_id]

    def get(self, agent_id: str) -> Any | None:
        return self.agents.get(agent_id)

    def all_agents(self) -> list[Any]:
        return list(self.agents.values())
