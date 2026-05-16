# runtime/gbrain/__init__.py


class GBrain:
    """Phase 7 unified GBrain interface for evolution/sandbox"""

    def __init__(self):
        from runtime.gbrain.cluster_detect import ClusterDetect
        from runtime.gbrain.relation_infer import RelationInfer
        from runtime.gbrain.semantic_gravity import SemanticGravity

        self.relation_infer = RelationInfer()
        self.cluster_detect = ClusterDetect()
        self.semantic_gravity = SemanticGravity()

    def analyze(self, completed_task_names):
        relations = self.relation_infer.infer(completed_task_names)
        clusters = self.cluster_detect.cluster(completed_task_names, relations)
        gravity = self.semantic_gravity.compute(clusters, relations)
        return {
            "relations": relations,
            "clusters": clusters,
            "gravity": gravity,
        }
