# runtime/specialization/semantic_affinity.py


class SemanticAffinityEngine:

    def compute_affinity(
        self,
        agent,
        concepts,
    ):

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
