# runtime/attention/global_attention_field.py

from collections import defaultdict


class GlobalAttentionField:

    def __init__(self):

        self.node_attention = defaultdict(float)

        self.agent_attention = defaultdict(
            lambda: defaultdict(float),
        )

    def reinforce(self, node_id, agent_id, value):

        self.node_attention[node_id] += value

        self.agent_attention[agent_id][node_id] += value

    def get_node_attention(self, node_id):

        return self.node_attention.get(node_id, 0.0)

    def get_agent_attention(self, agent_id, node_id):

        return self.agent_attention[agent_id].get(node_id, 0.0)

    def hottest_nodes(self, top_k=10):

        return sorted(
            self.node_attention.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:top_k]

    def avg_latency(self):

        return 0.1

    def avg_coherence(self):

        if not self.node_attention:
            return 0.5

        values = list(self.node_attention.values())

        return min(1.0, sum(values) / len(values) / 10.0)

    def memory_hit_rate(self):

        if not self.node_attention:
            return 0.0

        hits = sum(1 for v in self.node_attention.values() if v > 0)

        return hits / len(self.node_attention)
