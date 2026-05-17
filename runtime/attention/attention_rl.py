"""Reinforcement learning module for attention affinity updates."""

from typing import Any


class AttentionRL:
    """Updates agent affinity scores using RL-style feedback with learning rate and decay."""

    def __init__(
        self,
        learning_rate: float = 0.1,
        decay_rate: float = 0.01,
        min_affinity: float = 0.0,
        max_affinity: float = 5.0,
    ) -> None:

        self.learning_rate = learning_rate
        self.decay_rate = decay_rate
        self.min_affinity = min_affinity
        self.max_affinity = max_affinity

    def update_agent_affinity(self, agent: Any, node_id: str, feedback_score: float) -> float:

        if not hasattr(agent.profile, "semantic_affinity"):
            agent.profile.semantic_affinity = {}

        old_value = agent.profile.semantic_affinity.get(node_id, 0.5)

        new_value = old_value + self.learning_rate * feedback_score

        new_value = max(
            self.min_affinity,
            min(self.max_affinity, new_value),
        )

        for key in list(agent.profile.semantic_affinity.keys()):
            if key != node_id:
                agent.profile.semantic_affinity[key] *= 1 - self.decay_rate

        agent.profile.semantic_affinity[node_id] = new_value

        return new_value
