# runtime/specialization/expertise_tracker.py


class ExpertiseTracker:

    def update_expertise(
        self,
        agent,
        concepts,
    ):

        profile = agent.profile

        profile.completed_tasks += 1

        profile.expertise_score += 0.1

        for c in concepts:

            profile.semantic_affinity[c] = profile.semantic_affinity.get(c, 0.0) + 0.2
