"""Global attention field tracking both node and agent attention levels."""

from collections import defaultdict


class GlobalAttentionField:
    """Maintains a global attention field with node-level and agent-level attention tracking."""

    def __init__(self) -> None:

        self.node_attention: defaultdict[str, float] = defaultdict(float)

        self.agent_attention: defaultdict[str, defaultdict[str, float]] = defaultdict(
            lambda: defaultdict(float),
        )

    def reinforce(self, node_id: str, agent_id: str, value: float) -> None:

        self.node_attention[node_id] += value

        self.agent_attention[agent_id][node_id] += value

    def get_node_attention(self, node_id: str) -> float:

        return self.node_attention.get(node_id, 0.0)

    def get_agent_attention(self, agent_id: str, node_id: str) -> float:

        return self.agent_attention[agent_id].get(node_id, 0.0)

    def hottest_nodes(self, top_k: int = 10) -> list[tuple[str, float]]:

        return sorted(
            self.node_attention.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:top_k]

    def avg_latency(self) -> float:

        return 0.1

    def avg_coherence(self) -> float:

        if not self.node_attention:
            return 0.5

        values = list(self.node_attention.values())

        return min(1.0, sum(values) / len(values) / 10.0)

    def memory_hit_rate(self) -> float:

        if not self.node_attention:
            return 0.0

        hits = sum(1 for v in self.node_attention.values() if v > 0)

        return hits / len(self.node_attention)
