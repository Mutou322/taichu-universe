"""Tracks agent expertise growth and concept exposure."""

from typing import Any


class ExpertiseTracker:
    """Updates agent expertise score and semantic affinity based on completed tasks."""

    def update_expertise(
        self,
        agent: Any,
        concepts: list[str],
    ) -> None:

        if not hasattr(agent, "profile"):
            return

        profile = agent.profile

        profile.completed_tasks += 1

        profile.expertise_score += 0.1

        for c in concepts:

            profile.semantic_affinity[c] = min(profile.semantic_affinity.get(c, 0.0) + 0.2, 5.0)
