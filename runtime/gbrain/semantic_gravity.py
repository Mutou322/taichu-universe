# runtime/gbrain/semantic_gravity.py


class SemanticGravity:
    def compute(self, clusters, relations):
        gravity = {}
        for cluster_id, nodes in clusters.items():
            gravity[cluster_id] = sum(len(relations.get(n, [])) for n in nodes)
        return gravity
