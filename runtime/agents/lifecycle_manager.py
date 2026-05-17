"""Manages agent spawn and destroy lifecycle."""

from typing import Any


class LifecycleManager:
    """Manages agent creation, registration, and destruction."""

    def __init__(self, registry: Any) -> None:

        self.registry = registry

    def spawn_agent(self, agent: Any) -> None:

        self.registry.register(agent)

    def destroy_agent(self, agent_id: str) -> bool:

        agent = self.registry.get(agent_id)

        if agent is None:
            return False

        agent.running = False
        self.registry.unregister(agent_id)

        return True
