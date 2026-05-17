"""图谱一致性引擎 — 计算图的孤儿比例、平均关系数与簇紧密度"""

import statistics
from collections import defaultdict


class GraphCoherenceEngine:
    """评估知识图谱的结构一致性，输出 coherence/orphan_ratio 等指标"""

    ROUND_PRECISION = 4

    def compute(self, graph_nodes):
        """统计孤立节点比例、平均关系数和簇内 gravity 标准差"""
        total_nodes = len(graph_nodes)
        if total_nodes == 0:
            return {
                "coherence": 0.0,
                "orphan_ratio": 0.0,
                "avg_relations": 0.0,
                "cluster_tightness": 0.0,
            }

        orphan_nodes = 0
        total_relations = 0
        clusters = defaultdict(list)

        for node in graph_nodes.values():
            relation_count = len(node.relations)
            total_relations += relation_count
            if relation_count == 0:
                orphan_nodes += 1
            for tag in node.metadata.get("tags", []):
                if tag and isinstance(tag, str):
                    clusters[tag].append(node.gravity)

        orphan_ratio = orphan_nodes / total_nodes
        avg_relations = total_relations / total_nodes

        # cluster tightness = 平均每个 cluster 内节点 gravity 的 std
        cluster_tightness = 0.0
        if clusters:
            tightness_values = []
            for g_list in clusters.values():
                if len(g_list) > 1:
                    tightness_values.append(statistics.stdev(g_list))
            cluster_tightness = sum(tightness_values) / len(tightness_values) if tightness_values else 0.0

        coherence = max(0.0, 1.0 - orphan_ratio)

        return {
            "coherence": round(coherence, self.ROUND_PRECISION),
            "orphan_ratio": round(orphan_ratio, self.ROUND_PRECISION),
            "avg_relations": round(avg_relations, self.ROUND_PRECISION),
            "cluster_tightness": round(cluster_tightness, self.ROUND_PRECISION),
        }


graph_coherence = GraphCoherenceEngine()
