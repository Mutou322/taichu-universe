# runtime/phase9_main.py
# Phase 9 — 主循环：完整整合 数据摄取 → Workflow → GBrain → GEP → Multi-Agent 自演化闭环

import asyncio

from runtime.agents.graph_agent import GraphAgent
from runtime.agents.memory_agent import MemoryAgent
from runtime.agents.registry import AgentRegistry
from runtime.agents.retrieval_agent import RetrievalAgent
from runtime.agents.synthesizer_agent import SynthesizerAgent
from runtime.attention.cluster_manager import ClusterManager
from runtime.attention.emergent_ecosystem import EmergentCognitiveEcosystem
from runtime.attention.global_attention_field import GlobalAttentionField
from runtime.attention.hotspot_clustering import HotspotClustering
from runtime.capabilities.capability import Capability
from runtime.capabilities.capability_matcher import CapabilityMatcher
from runtime.capabilities.capability_registry import CapabilityRegistry
from runtime.evolution.evolution_engine import EvolutionEngine
from runtime.evolution.genome import Genome
from runtime.gbrain.semantic_intelligence import GBrain
from runtime.ingestion.data_ingest import ContinuousIngest
from runtime.metrics.metrics_bus import metrics_bus
from runtime.planning.workflow_executor import ContinuousWorkflowExecutor
from runtime.scheduler.adaptive_scheduler import AdaptiveScheduler


class DummySource:

    def __init__(self, docs, loop=True):
        self.docs = docs
        self.loop = loop
        self.idx = 0

    async def fetch(self):
        doc = self.docs[self.idx % len(self.docs)]
        self.idx += 1
        return doc


class SimpleGraph:

    def __init__(self):
        self.nodes = {}

    def add_node(self, doc, embedding=None):
        nid = f"n{len(self.nodes)}"
        self.nodes[nid] = {"text": doc, "embedding": embedding}

    def all_nodes(self):
        return self.nodes


async def phase9_main_loop(ingest_sources, agents, graph, registry, cap_reg, num_ticks=10):

    # 1. MetricsBus（全局单例）

    # 2. GBrain
    gbrain = GBrain()

    # 3. Attention + Ecosystem
    field = GlobalAttentionField()
    cluster_mgr = ClusterManager(n_clusters=3)
    hotspot = HotspotClustering(min_attention=2.0)

    ecosystem = EmergentCognitiveEcosystem(
        cluster_manager=cluster_mgr,
        attention_field=field,
        hotspot_clustering=hotspot,
        metrics_bus=metrics_bus,
        registry=registry,
    )
    ecosystem.gbrain = gbrain

    # 4. Evolution Engine
    base_genome = Genome(
        vector_top_k=8,
        graph_depth=2,
        rerank_weight=0.6,
        memory_decay=0.95,
    )
    evolution_engine = EvolutionEngine(base_genome, metrics_bus, gbrain)

    # 5. Adaptive Scheduler
    scheduler = AdaptiveScheduler(agents)

    # 6. Workflow Executor
    executor = ContinuousWorkflowExecutor(
        scheduler,
        ecosystem,
        evolution_engine,
        metrics_bus,
    )

    # 7. 启动长期 ingestion（background）
    ingest = ContinuousIngest(ingest_sources, graph)
    asyncio.create_task(ingest.run())

    # 8. 主循环
    tick = 0
    while tick < num_ticks:

        # 注入一些 attention 到 field（模拟 workflow 产生的节点）
        for i in range(3):
            field.reinforce(f"tick_{tick}_node_{i}", agents[i % len(agents)].agent_id, 1.0)

        print(f"[Phase 9] Tick {tick} running...")

        await executor.run_tick()

        # GBrain 分析（每 3 tick）
        if tick > 0 and tick % 3 == 0:
            graph_nodes = graph.all_nodes()
            if graph_nodes:
                relations, clusters, gravity = gbrain.analyze(graph_nodes)
                print(
                    f"  GBrain: {len(relations)} relations, "
                    f"{len(clusters)} clusters, "
                    f"{len(gravity)} gravity values"
                )

                metrics_bus.emit(
                    "gbrain",
                    {
                        "clusters": clusters,
                        "gravity": gravity,
                    },
                )

        # 打印状态
        if tick % 5 == 0:
            print(
                f"  Gen: {evolution_engine.generation}, "
                f"Graph nodes: {len(graph.all_nodes())}, "
                f"Ingested: {ingest.total_ingested if hasattr(ingest, 'total_ingested') else 'N/A'}"
            )

        tick += 1
        await asyncio.sleep(0.5)

    print(f"\n[Phase 9] Completed {num_ticks} ticks.")
    print(f"  Evolution Generations: {evolution_engine.generation}")
    print(f"  Graph Nodes: {len(graph.all_nodes())}")
    print(
        f"  Best Genome: vtk={base_genome.vector_top_k}, "
        f"gd={base_genome.graph_depth}, "
        f"rw={base_genome.rerank_weight:.2f}, "
        f"md={base_genome.memory_decay:.2f}"
    )

    return ecosystem, evolution_engine


async def main():

    registry = AgentRegistry()
    cap_reg = CapabilityRegistry()

    agents = [
        RetrievalAgent("retrieval_agent"),
        GraphAgent("graph_agent"),
        MemoryAgent("memory_agent"),
        SynthesizerAgent("synth_agent"),
    ]
    for a in agents:
        registry.register(a)
        a.profile.semantic_affinity = {type(a).__name__.replace("Agent", "").lower(): 0.8}
        a.genome = Genome()

    cap_reg.register("retrieval_agent", [Capability("retrieval")])
    cap_reg.register("graph_agent", [Capability("graph_analysis")])
    cap_reg.register("memory_agent", [Capability("memory")])
    cap_reg.register("synth_agent", [Capability("synthesis")])

    # 数据源
    docs_pool = [
        "Attention collapse in transformer models with long sequences.",
        "KV cache optimization reduces memory overhead significantly.",
        "Scaling laws predict model performance based on compute budget.",
        "Flash attention provides efficient attention computation.",
        "Position encoding enables transformers to handle order.",
        "Mixture of experts reduces computational cost in large models.",
    ]
    source = DummySource(docs_pool)
    graph = SimpleGraph()

    await phase9_main_loop(
        ingest_sources=[source],
        agents=agents,
        graph=graph,
        registry=registry,
        cap_reg=cap_reg,
        num_ticks=10,
    )


if __name__ == "__main__":
    asyncio.run(main())
