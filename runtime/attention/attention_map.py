"""Bidirectional attention map: node-to-agent weight matrix."""

from collections import defaultdict
from typing import Any


class AttentionMap:
    """Stores and queries attention weights between nodes and agents."""

    def __init__(self) -> None:

        # node_id -> agent_id -> weight
        self.map: defaultdict[str, defaultdict[str, float]] = defaultdict(lambda: defaultdict(float))

    def set_weight(self, node_id: str, agent_id: str, weight: float) -> None:

        self.map[node_id][agent_id] = weight

    def get_weight(self, node_id: str, agent_id: str) -> float:

        return self.map[node_id].get(agent_id, 0.0)

    def top_agent_for_node(self, node_id: str) -> str | None:

        agents = self.map[node_id]

        if not agents:
            return None

        return max(agents.items(), key=lambda x: x[1])[0]

    def all_weights(self) -> Any:

        return self.map
