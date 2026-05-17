"""聚类检测 — 基于哈希分桶的简易图节点聚类"""


class ClusterDetect:
    """使用哈希取模将节点分配到固定数量的簇中"""

    NUM_CLUSTERS = 5

    def cluster(self, nodes, relations):
        """对节点按哈希值分桶，返回 {cluster_id: [nodes]} 映射"""
        clusters = {}
        for node in nodes:
            cluster_id = hash(node) % self.NUM_CLUSTERS
            clusters.setdefault(cluster_id, []).append(node)
        return clusters
