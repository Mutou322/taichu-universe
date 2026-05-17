"""语义引力 — 基于节点簇内关系密度计算每个簇的引力值"""


class SemanticGravity:
    """计算图簇的语义引力：簇内节点的关系数之和"""

    def compute(self, clusters: dict, relations: dict) -> dict:
        """计算每个簇的引力值 = 簇内所有节点的关系数之和"""
        gravity = {}
        for cluster_id, nodes in clusters.items():
            gravity[cluster_id] = sum(len(relations.get(n, [])) for n in nodes)
        return gravity

    def tick(self, graph_nodes: dict | list) -> dict:
        """包装 compute() 以兼容 GravityScheduler 的调用。"""
        if isinstance(graph_nodes, dict):
            clusters = {0: list(graph_nodes.keys())}
        else:
            clusters = {0: list(range(len(graph_nodes)))}
        relations: dict = {}
        return self.compute(clusters, relations)
