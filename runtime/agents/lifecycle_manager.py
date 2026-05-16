# runtime/agents/lifecycle_manager.py


class LifecycleManager:

    def __init__(self, registry):

        self.registry = registry

    def spawn_agent(self, agent):

        self.registry.register(agent)

    def destroy_agent(self, agent_id):

        agent = self.registry.get(agent_id)

        if agent is None:
            return False

        agent.running = False
        self.registry.unregister(agent_id)

        return True
