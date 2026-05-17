"""结构调度器 — 定时执行图结构分析：关系推断→聚类→本体构建"""

import asyncio

from runtime.gbrain.cluster_detect import ClusterDetect as ClusterDetector
from runtime.gbrain.cluster_metrics import emit_cluster_metrics
from runtime.gbrain.ontology_builder import OntologyBuilder
from runtime.gbrain.ontology_metrics import emit_ontology_metrics
from runtime.gbrain.relation_infer import RelationInfer as RelationInferEngine


class StructureScheduler:
    """按固定间隔循环执行关系推断、聚类检测和本体构建并推送指标"""

    def __init__(self, graph) -> None:
        self.graph = graph
        self.relation_engine = RelationInferEngine()
        self.cluster_engine = ClusterDetector()
        self.ontology_builder = OntologyBuilder()
        self.running = False

    async def start(self) -> None:
        self.running = True
        while self.running:

            # 1️⃣ infer relations
            all_nodes = list(self.graph.nodes.values())
            inferred = self.relation_engine.infer(all_nodes)

            # 2️⃣ detect clusters
            clusters = self.cluster_engine.cluster(all_nodes, inferred)
            await emit_cluster_metrics(clusters)

            # 3️⃣ build ontology
            ontology = self.ontology_builder.build(self.graph.nodes)
            await emit_ontology_metrics(ontology)

            await asyncio.sleep(5)

    def stop(self) -> None:
        self.running = False
