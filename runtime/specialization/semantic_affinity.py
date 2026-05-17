"""Computes semantic affinity between agents and task concepts."""

from typing import Any


class SemanticAffinityEngine:
    """Calculates affinity score using semantic affinity vectors and domain matching."""

    def compute_affinity(
        self,
        agent: Any,
        concepts: list[str],
    ) -> float:

        if not hasattr(agent, "profile"):
            return 0.0

        profile = agent.profile

        score = 0.0

        for c in concepts:

            score += profile.semantic_affinity.get(
                c,
                0.0,
            )

            # 双向匹配：domain 在概念中，或者概念在 domain 中
            domain_lower = profile.primary_domain.lower()
            concept_lower = c.lower()

            if domain_lower in concept_lower or concept_lower in domain_lower:
                score += 2.0

        return score
