# runtime/gbrain/graph_coherence.py

import statistics
from collections import defaultdict


class GraphCoherenceEngine:

    def compute(self, graph_nodes):
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
            "coherence": round(coherence, 4),
            "orphan_ratio": round(orphan_ratio, 4),
            "avg_relations": round(avg_relations, 4),
            "cluster_tightness": round(cluster_tightness, 4),
        }


graph_coherence = GraphCoherenceEngine()
