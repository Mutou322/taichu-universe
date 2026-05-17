"""KMeans-based clustering of agents and workflow nodes."""

from typing import Any

import numpy as np
from sklearn.cluster import KMeans


class ClusterManager:
    """Clusters agents by attention vectors and nodes by attention field values."""

    def __init__(self, n_clusters: int = 3) -> None:

        self.n_clusters = n_clusters

        self.agent_clusters: dict[str, int] = {}

        self.node_clusters: dict[str, int] = {}

    def cluster_agents(self, agents: list[Any]) -> dict[str, int]:

        if not agents:
            return self.agent_clusters

        # 收集所有 task_type key，统一向量维度
        all_keys = set()
        for agent in agents:
            vec = agent.attention_vector()
            if isinstance(vec, dict):
                all_keys.update(vec.keys())

        all_keys = sorted(all_keys)

        # 构建统一长度的向量
        X = []
        for agent in agents:
            vec = agent.attention_vector()
            if isinstance(vec, dict):
                row = [vec.get(k, 0.0) for k in all_keys]
            else:
                row = [0.0] * len(all_keys) if all_keys else [0.0]
            X.append(row)

        X = np.array(X)

        if len(X) < self.n_clusters:
            self.n_clusters = max(1, len(X))

        if len(X) <= 1:
            for agent in agents:
                self.agent_clusters[agent.agent_id] = 0
            return self.agent_clusters

        kmeans = KMeans(
            n_clusters=self.n_clusters,
            random_state=42,
            n_init="auto",
        )

        labels = kmeans.fit_predict(X)

        for i, agent in enumerate(agents):

            self.agent_clusters[agent.agent_id] = int(labels[i])

        return self.agent_clusters

    def cluster_nodes(self, field: Any) -> dict[str, int]:

        nodes = list(field.node_attention.keys())

        if not nodes:
            return self.node_clusters

        values = np.array(
            [field.node_attention[n] for n in nodes],
        ).reshape(-1, 1)

        if len(values) < self.n_clusters:
            self.n_clusters = max(1, len(values))

        if len(values) == 1:
            self.node_clusters[nodes[0]] = 0
            return self.node_clusters

        kmeans = KMeans(
            n_clusters=self.n_clusters,
            random_state=42,
            n_init="auto",
        )

        labels = kmeans.fit_predict(values)

        for i, node in enumerate(nodes):

            self.node_clusters[node] = int(labels[i])

        return self.node_clusters
