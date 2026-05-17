"""关系推断 — 基于名称前缀相似度推断节点间关联关系"""

from typing import Any


def _node_label(node: Any) -> str:
    """统一获取节点标签用于首字符比较"""
    if isinstance(node, str):
        return node[:1]
    return (getattr(node, "label", None) or getattr(node, "id", None) or str(node))[:1]


class RelationInfer:
    """按名称首字符相似度推断节点间的潜在关系"""

    SIMILARITY_THRESHOLD = 0.5
    SAME_PREFIX_SCORE = 0.6
    DIFF_PREFIX_SCORE = 0.3

    def infer(self, graph_nodes):
        """返回 {node: [similar_nodes]} 映射，仅保留高于阈值的相似节点"""
        relations = {}
        for node in graph_nodes:
            relations[node] = [
                n for n in graph_nodes if n != node and self.similarity(node, n) > self.SIMILARITY_THRESHOLD
            ]
        return relations

    def similarity(self, node_a, node_b):
        return self.SAME_PREFIX_SCORE if _node_label(node_a) == _node_label(node_b) else self.DIFF_PREFIX_SCORE
