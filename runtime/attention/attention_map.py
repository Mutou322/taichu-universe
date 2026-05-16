# runtime/attention/attention_map.py

from collections import defaultdict


class AttentionMap:

    def __init__(self):

        # node_id -> agent_id -> weight
        self.map = defaultdict(lambda: defaultdict(float))

    def set_weight(self, node_id, agent_id, weight):

        self.map[node_id][agent_id] = weight

    def get_weight(self, node_id, agent_id):

        return self.map[node_id].get(agent_id, 0.0)

    def top_agent_for_node(self, node_id):

        agents = self.map[node_id]

        if not agents:
            return None

        return max(agents.items(), key=lambda x: x[1])[0]

    def all_weights(self):

        return self.map
