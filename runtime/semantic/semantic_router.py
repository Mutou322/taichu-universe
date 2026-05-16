# runtime/semantic/semantic_router.py


class SemanticRouter:

    def route(self, task, agents):
        concepts = task.payload.get("concepts", [])
        scored = []

        for agent in agents:
            score = 0
            for c in concepts:
                if c.lower() in agent.agent_id.lower():
                    score += 1
            scored.append((score, agent))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]
