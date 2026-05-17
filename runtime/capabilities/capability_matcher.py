"""Matches tasks to agents based on capability scores and load."""

from typing import Any

from runtime.capabilities.capability_score import CapabilityScore


class CapabilityMatcher:
    """Selects the best agent for a task by scoring capabilities and penalizing load."""

    def __init__(self, registry: Any) -> None:

        self.registry = registry
        self.scorer = CapabilityScore()

    def select_agent(self, task: Any, agents: list[Any]) -> Any | None:

        scored = []

        for agent in agents:

            capabilities = self.registry.get(agent.agent_id)

            capability_score = self.scorer.score(task, capabilities)

            load_penalty = getattr(agent, "load", 0) * 0.3

            final_score = capability_score - load_penalty

            scored.append((final_score, agent))

        scored.sort(key=lambda x: x[0], reverse=True)
        if not scored:
            return None
        return scored[0][1]
