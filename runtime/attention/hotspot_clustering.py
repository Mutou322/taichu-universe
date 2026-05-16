# runtime/attention/hotspot_clustering.py

from collections import defaultdict


class HotspotClustering:

    def __init__(self, min_attention=3.0):

        self.min_attention = min_attention

        self.clusters = defaultdict(list)

    def form_clusters(self, node_attention_map):

        self.clusters = defaultdict(list)

        hotspots = {n: v for n, v in node_attention_map.items() if v >= self.min_attention}

        for node, value in hotspots.items():

            cluster_id = int(value)

            self.clusters[cluster_id].append((node, value))

        return self.clusters
