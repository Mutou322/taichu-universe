"""Clusters attention hotspots by intensity value."""

from collections import defaultdict
from typing import Any


class HotspotClustering:
    """Groups high-attention nodes into clusters bucketed by attention value."""

    def __init__(self, min_attention: float = 3.0) -> None:

        self.min_attention = min_attention

        self.clusters: defaultdict[int, list[Any]] = defaultdict(list)

    def form_clusters(self, node_attention_map: dict[str, float]) -> Any:

        self.clusters = defaultdict(list)

        hotspots = {n: v for n, v in node_attention_map.items() if v >= self.min_attention}

        for node, value in hotspots.items():

            cluster_id = int(value)

            self.clusters[cluster_id].append((node, value))

        return self.clusters
