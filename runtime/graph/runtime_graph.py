# runtime/graph/runtime_graph.py

from runtime.gbrain.semantic_types import SemanticNode


class RuntimeGraph:

    def __init__(self):
        self.nodes = {}

    def add_node(self, node_id: str, label: str):
        if node_id not in self.nodes:
            self.nodes[node_id] = SemanticNode(id=node_id, label=label)

    def add_relation(self, source: str, target: str):
        if source in self.nodes:
            self.nodes[source].relations.append(target)
