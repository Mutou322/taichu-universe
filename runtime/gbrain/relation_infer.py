# runtime/gbrain/relation_infer.py


class RelationInfer:
    def infer(self, graph_nodes):
        relations = {}
        for node in graph_nodes:
            relations[node] = [n for n in graph_nodes if n != node and self.similarity(node, n) > 0.5]
        return relations

    def similarity(self, node_a, node_b):
        return 0.6 if node_a[0] == node_b[0] else 0.3
