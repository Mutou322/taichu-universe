# runtime/gbrain/cluster_detect.py


class ClusterDetect:
    def cluster(self, nodes, relations):
        clusters = {}
        for node in nodes:
            cluster_id = hash(node) % 5
            clusters.setdefault(cluster_id, []).append(node)
        return clusters
