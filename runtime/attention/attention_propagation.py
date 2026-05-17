"""Propagates attention from source nodes to dependent neighbors."""

from typing import Any


class AttentionPropagation:
    """Recursively propagates attention values along workflow dependency edges."""

    def __init__(self, propagation_rate: float = 0.3, max_depth: int = 2) -> None:

        self.propagation_rate = propagation_rate
        self.max_depth = max_depth

    def propagate(self, field: Any, workflow: Any, source_node: str, value: float, depth: int = 0) -> None:

        if depth >= self.max_depth:
            return

        # 依赖 source_node 的节点是邻居
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
