# runtime/gbrain/structure_scheduler.py

import asyncio

from runtime.gbrain.cluster_detect import ClusterDetect as ClusterDetector
from runtime.gbrain.cluster_metrics import emit_cluster_metrics
from runtime.gbrain.ontology_builder import OntologyBuilder
from runtime.gbrain.ontology_metrics import emit_ontology_metrics
from runtime.gbrain.relation_infer import RelationInfer as RelationInferEngine


class StructureScheduler:

    def __init__(self, graph):
        self.graph = graph
        self.relation_engine = RelationInferEngine()
        self.cluster_engine = ClusterDetector()
        self.ontology_builder = OntologyBuilder()
        self.running = False

    async def start(self):
        self.running = True
        while self.running:

            # 1️⃣ infer relations
            for source in self.graph.nodes.values():
                for target in self.graph.nodes.values():
                    if source.id == target.id:
                        continue
                    new_relations = self.relation_engine.infer(source, target)
                    for r in new_relations:
                        if r.target not in source.relations:
                            source.relations.append(r.target)

            # 2️⃣ detect clusters
            clusters = self.cluster_engine.detect(self.graph.nodes)
            await emit_cluster_metrics(clusters)

            # 3️⃣ build ontology
            ontology = self.ontology_builder.build(self.graph.nodes)
            await emit_ontology_metrics(ontology)

            await asyncio.sleep(5)

    def stop(self):
        self.running = False
