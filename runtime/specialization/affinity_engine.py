# runtime/specialization/affinity_engine.py


class AffinityRouter:

    def __init__(self, affinity_engine):

        self.affinity_engine = affinity_engine

    def select_best_agent(
        self,
        task,
        agents,
    ):

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

        return scored[0][1]
