# runtime/capabilities/capability_matcher.py

from runtime.capabilities.capability_score import CapabilityScore


class CapabilityMatcher:

    def __init__(self, registry):

        self.registry = registry
        self.scorer = CapabilityScore()

    def select_agent(self, task, agents):

        scored = []

        for agent in agents:

            capabilities = self.registry.get(agent.agent_id)

            capability_score = self.scorer.score(task, capabilities)

            load_penalty = getattr(agent, "load", 0) * 0.3

            final_score = capability_score - load_penalty

            scored.append((final_score, agent))

        scored.sort(key=lambda x: x[0], reverse=True)

        return scored[0][1]
