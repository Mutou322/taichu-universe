# runtime/attention/attention_propagation.py


class AttentionPropagation:

    def __init__(self, propagation_rate=0.3, max_depth=2):

        self.propagation_rate = propagation_rate
        self.max_depth = max_depth

    def propagate(self, field, workflow, source_node, value, depth=0):

        if depth >= self.max_depth:
            return

        # 邻居 = 依赖此节点 + 此节点依赖的节点
        neighbors = set()

        for nid, n in workflow.nodes.items():

            if source_node in n.dependencies:
                neighbors.add(nid)

            if nid in workflow.nodes.get(source_node, type("", (), {"dependencies": []})()).dependencies:
                pass  # 已经处理

        # 更准确的：依赖 source_node 的节点才是邻居
        neighbors = [nid for nid, n in workflow.nodes.items() if source_node in n.dependencies]

        for neighbor in neighbors:

            propagated = value * self.propagation_rate

            field.node_attention[neighbor] += propagated

            self.propagate(
                field,
                workflow,
                neighbor,
                propagated,
                depth + 1,
            )
