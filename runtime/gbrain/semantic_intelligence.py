"""GBrain — 语义智能总控：关系推断 → 聚类 → 引力计算 → 本体构建"""

from runtime.gbrain.cluster_detect import ClusterDetect
from runtime.gbrain.ontology_builder import ontology_builder
from runtime.gbrain.relation_infer import RelationInfer
from runtime.gbrain.semantic_gravity import SemanticGravity


class GBrain:
    """语义智能引擎，串联关系推断、聚类、引力计算和本体构建全流程"""

    def __init__(self) -> None:

        self.relation_infer = RelationInfer()
        self.cluster_detect = ClusterDetect()
        self.semantic_gravity = SemanticGravity()
        self.ontology_builder = ontology_builder

    def analyze(self, graph_nodes: list) -> tuple:
        """执行完整分析链路，返回 (relations, clusters, gravity) 三元组"""
        relations = self.relation_infer.infer(graph_nodes)

        clusters = self.cluster_detect.cluster(graph_nodes, relations)

        gravity = self.semantic_gravity.compute(clusters, relations)

        self.ontology_builder.build(graph_nodes)  # type: ignore[arg-type]

        return relations, clusters, gravity
