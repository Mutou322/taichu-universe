# runtime/attention/emergent_ecosystem.py

import asyncio
from collections import defaultdict


class EmergentCognitiveEcosystem:

    def __init__(self, cluster_manager, attention_field, hotspot_clustering, metrics_bus, registry=None):

        self.cluster_manager = cluster_manager
        self.attention_field = attention_field
        self.hotspot_clustering = hotspot_clustering
        self.metrics_bus = metrics_bus
        self.registry = registry

        self.semantic_gravity = defaultdict(float)

        self.agent_influence = defaultdict(float)

    def select_agent(self, node):
        """Phase 9: 为节点选择最合适的 agent"""
        if self.registry is None:
            return None
        agents = self.registry.all_agents()
        if not agents:
            return None
        # 简单策略：选 load 最低的 agent
        return min(agents, key=lambda a: getattr(a, "load", 0))

    async def update(self, agents):

        # 1. Update clusters
        self.cluster_manager.cluster_agents(agents)
        self.cluster_manager.cluster_nodes(self.attention_field)

        # 2. Update hotspot clusters
        self.hotspot_clusters = self.hotspot_clustering.form_clusters(
            self.attention_field.node_attention,
        )

        # 3. Compute semantic gravity
        self.compute_semantic_gravity(agents)

        # 4. Reinforce attention based on cluster influence
        self.reinforce_clusters(agents)

        # 5. Emit metrics to Nebula UI
        await self.emit_metrics()

    def compute_semantic_gravity(self, agents):

        for node_id, att in self.attention_field.node_attention.items():

            cluster_id = self.cluster_manager.node_clusters.get(node_id, 0)

            cluster_bonus = 0.1 * sum(
                self.attention_field.get_agent_attention(
                    agent.agent_id,
                    node_id,
                )
                for agent in agents
                if self.cluster_manager.agent_clusters.get(agent.agent_id) == cluster_id
            )

            self.semantic_gravity[node_id] = att + cluster_bonus

    def reinforce_clusters(self, agents):

        for agent in agents:

            for node_id in self.semantic_gravity:

                influence = 0.05 * self.semantic_gravity[node_id]

                self.attention_field.reinforce(
                    node_id,
                    agent.agent_id,
                    influence,
                )

                self.agent_influence[agent.agent_id] += influence

    async def emit_metrics(self):

        await self.metrics_bus.emit_async(
            "ecosystem",
            {
                "node_clusters": self.cluster_manager.node_clusters,
                "agent_clusters": self.cluster_manager.agent_clusters,
                "hotspot_clusters": self.hotspot_clusters,
                "semantic_gravity": dict(self.semantic_gravity),
                "agent_influence": dict(self.agent_influence),
            },
        )
