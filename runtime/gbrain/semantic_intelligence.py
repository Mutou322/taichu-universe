# runtime/gbrain/semantic_intelligence.py

from runtime.gbrain.cluster_detect import ClusterDetect
from runtime.gbrain.ontology_builder import ontology_builder
from runtime.gbrain.relation_infer import RelationInfer
from runtime.gbrain.semantic_gravity import SemanticGravity


class GBrain:

    def __init__(self):

        self.relation_infer = RelationInfer()
        self.cluster_detect = ClusterDetect()
        self.semantic_gravity = SemanticGravity()
        self.ontology_builder = ontology_builder

    def analyze(self, graph_nodes):

        relations = self.relation_infer.infer(graph_nodes)

        clusters = self.cluster_detect.cluster(graph_nodes, relations)

        gravity = self.semantic_gravity.compute(clusters, relations)

        self.ontology_builder.build(graph_nodes)

        return relations, clusters, gravity
