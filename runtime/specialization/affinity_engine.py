"""Routes tasks to agents based on computed semantic affinity."""

from typing import Any


class AffinityRouter:
    """Selects the best agent for a task using affinity scores and load balancing."""

    def __init__(self, affinity_engine: Any) -> None:

        self.affinity_engine = affinity_engine

    def select_best_agent(
        self,
        task: Any,
        agents: list[Any],
    ) -> Any | None:

        concepts = task.payload.get(
            "concepts",
            [],
        )

        scored = []

        for agent in agents:

            affinity = self.affinity_engine.compute_affinity(
                agent,
                concepts,
            )

            load_penalty = getattr(agent, "load", 0) * 0.5

            final_score = affinity - load_penalty

            scored.append((final_score, agent))

        scored.sort(
            key=lambda x: x[0],
            reverse=True,
        )
        if not scored:
            return None
        return scored[0][1]
