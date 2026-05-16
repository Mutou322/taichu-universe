# runtime/capabilities/capability_registry.py


class CapabilityRegistry:

    def __init__(self):

        self.agent_capabilities = {}

    def register(self, agent_id, capabilities):

        self.agent_capabilities[agent_id] = capabilities

    def get(self, agent_id):

        return self.agent_capabilities.get(agent_id, [])
