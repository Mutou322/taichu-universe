# runtime/agents/registry.py


class AgentRegistry:

    def __init__(self):
        self.agents = {}

    def register(self, agent):
        self.agents[agent.agent_id] = agent

    def unregister(self, agent_id):
        if agent_id in self.agents:
            del self.agents[agent_id]

    def get(self, agent_id):
        return self.agents.get(agent_id)

    def all_agents(self):
        return list(self.agents.values())
