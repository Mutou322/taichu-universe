# runtime/attention/attention_routing.py


class AttentionRouting:

    def __init__(self, attention_map, matcher, registry):

        self.attention_map = attention_map
        self.matcher = matcher
        self.registry = registry

    def select_agent_for_node(self, node):

        agents_sorted = sorted(
            self.attention_map.all_weights()[node.node_id].items(),
            key=lambda x: x[1],
            reverse=True,
        )

        for agent_id, _ in agents_sorted:

            agent = self.registry.get(agent_id)

            if getattr(agent, "load", 0) < 3:

                return agent

        return self.matcher.select_agent(
            node,
            self.registry.all_agents(),
        )
