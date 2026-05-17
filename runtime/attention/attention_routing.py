"""Routes workflow nodes to agents based on attention weights."""

from typing import Any


class AttentionRouting:
    """Selects the best agent for a workflow node using attention map and load balancing."""

    def __init__(self, attention_map: Any, matcher: Any, registry: Any) -> None:

        self.attention_map = attention_map
        self.matcher = matcher
        self.registry = registry

    def select_agent_for_node(self, node: Any) -> Any | None:

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
