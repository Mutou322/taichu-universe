"""Reinforces agent affinity based on task success feedback."""

from typing import Any


class AffinityLearning:
    """Updates agent semantic affinity after completing a task of a given type."""

    def reinforce(self, agent: Any, task_type: str, success_score: float) -> None:

        if not hasattr(agent, "profile"):
            return

        profile = agent.profile

        current = profile.semantic_affinity.get(task_type, 0.0) + success_score
        profile.semantic_affinity[task_type] = min(current, 5.0)
