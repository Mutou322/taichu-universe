"""Phase 9 归档运行时：Archive → 数据摄取 → 嵌入 → 图谱 → Multi-Agent → GBrain → GEP → Nebula UI 全链路"""

import asyncio
from pathlib import Path

from runtime.agents.graph_agent import GraphAgent
from runtime.agents.memory_agent import MemoryAgent
from runtime.agents.registry import AgentRegistry
from runtime.agents.retrieval_agent import RetrievalAgent
from runtime.agents.synthesizer_agent import SynthesizerAgent

# ---------------- Archive Layer ----------------
from runtime.archive.archive_manager import ArchiveManager
from runtime.attention.cluster_manager import ClusterManager
from runtime.attention.emergent_ecosystem import EmergentCognitiveEcosystem
from runtime.attention.global_attention_field import GlobalAttentionField
from runtime.attention.hotspot_clustering import HotspotClustering
from runtime.capabilities.capability import Capability
from runtime.capabilities.capability_registry import CapabilityRegistry
from runtime.evolution.evolution_engine import EvolutionEngine
from runtime.evolution.genome import Genome
from runtime.gbrain.semantic_intelligence import GBrain

# ---------------- Ingestion ----------------
from runtime.ingestion.semantic_embedding import SemanticEmbedder
from runtime.metrics.metrics_bus import metrics_bus
from runtime.planning.dynamic_decomposer import DynamicTaskDecomposer

# ---------------- Phase 9 核心 ----------------
from runtime.planning.workflow_executor import ContinuousWorkflowExecutor
from runtime.scheduler.adaptive_scheduler import AdaptiveScheduler


class SimpleGraph:
    """简易内存图谱，存储文件节点及其嵌入向量"""

    def __init__(self):
        self.nodes = {}

    def add_node(self, name, embedding=None):
        nid = f"n{len(self.nodes)}"
        self.nodes[nid] = {"name": name, "embedding": embedding}

    def all_nodes(self):
        return self.nodes


class FileSource:
    """文件数据源，从磁盘路径循环读取内容"""

    def __init__(self, paths):
        self.paths = paths
        self.idx = 0

    async def fetch(self):
        if not self.paths:
            return ""
        p = Path(self.paths[self.idx % len(self.paths)])
        self.idx += 1
        if p.exists():
            return p.read_text(encoding="utf-8", errors="replace")
        return f"content for {p.name}"


async def phase9_archive_main(file_sources):

    # ---------- 准备 Agent ----------
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
        a.profile.semantic_affinity = {
            type(a).__name__.replace("Agent", "").lower(): 0.8,
        }
        a.genome = Genome()

    cap_reg.register("retrieval_agent", [Capability("retrieval")])
    cap_reg.register("graph_agent", [Capability("graph_analysis")])
    cap_reg.register("memory_agent", [Capability("memory")])
    cap_reg.register("synth_agent", [Capability("synthesis")])

    # ---------- 1. Archive ----------
    archive = ArchiveManager()

    # ---------- 2. Graph ----------
    graph = SimpleGraph()

    # ---------- 3. Embedder ----------
    embedder = SemanticEmbedder()

    # ---------- 4. Metrics (全局单例) ----------

    # ---------- 5. GBrain ----------
    gbrain = GBrain()

    # ---------- 6. Ecosystem ----------
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

    # ---------- 7. Evolution Engine ----------
    base_genome = Genome(
        vector_top_k=8,
        graph_depth=2,
        rerank_weight=0.6,
        memory_decay=0.95,
    )
    evolution_engine = EvolutionEngine(base_genome, metrics_bus, gbrain)

    # ---------- 8. Scheduler ----------
    scheduler = AdaptiveScheduler(agents)

    # ---------- 9. Workflow Executor ----------
    executor = ContinuousWorkflowExecutor(
        scheduler,
        ecosystem,
        evolution_engine,
        metrics_bus,
    )

    # ---------- 10. Ingestion Loop ----------
    async def ingest_loop():

        while True:

            for file_path_str in file_sources:

                fp = Path(file_path_str)

                if not fp.exists():
                    continue

                # Archive
                archive_id = archive.store_file(
                    fp,
                    source_url=str(fp.resolve()),
                )

                # Embedding
                content = fp.read_text(encoding="utf-8", errors="replace")
                embeddings = embedder.embed_documents([content])

                # Update manifest
                archive.update_manifest(
                    archive_id,
                    embedding_ids=[f"emb_{archive_id}"],
                )

                # Update graph
                graph.add_node(fp.name, embedding=embeddings[0])

                # Metrics
                metrics_bus.emit(
                    "ingestion",
                    {
                        "archive_id": archive_id,
                        "file": fp.name,
                    },
                )

                print(f"  [Ingest] Archived: {fp.name} -> {archive_id}")

            await asyncio.sleep(5)

    asyncio.create_task(ingest_loop())

    # ---------- 11. 主循环 ----------
    decomposer = DynamicTaskDecomposer()
    tick = 0

    print("=== Phase 9 Archive Runtime ===")
    print(f"  Watching {len(file_sources)} file sources")
    print(f"  {len(agents)} agents")

    while tick < 20:

        # 模拟 workflow 节点
        for i in range(2):
            field.reinforce(
                f"tick_{tick}_n{i}",
                agents[i % len(agents)].agent_id,
                1.0,
            )

        print(f"[Tick {tick}] running...")

        await executor.run_tick()

        # GBrain analysis (每 3 tick)
        if tick > 0 and tick % 3 == 0:
            gnodes = graph.all_nodes()
            if gnodes:
                relations, clusters, gravity = gbrain.analyze(gnodes)
                print(f"  GBrain: {len(relations)} relations, " f"{len(clusters)} clusters")

                metrics_bus.emit(
                    "gbrain",
                    {
                        "clusters": clusters,
                        "gravity": gravity,
                    },
                )

        # Archive 状态
        manifests = archive.list_archives()
        graph_nodes = len(graph.all_nodes())
        print(f"  Archives: {len(manifests)}, Graph nodes: {graph_nodes}, " f"Gen: {evolution_engine.generation}")

        tick += 1
        await asyncio.sleep(0.5)

    print("\n=== Final State ===")
    print(f"Archives stored: {len(archive.list_archives())}")
    print(f"Graph nodes: {len(graph.all_nodes())}")
    print(f"Evolution generations: {evolution_engine.generation}")
    print(
        f"Best Genome: vtk={base_genome.vector_top_k}, "
        f"gd={base_genome.graph_depth}, "
        f"rw={base_genome.rerank_weight:.2f}, "
        f"md={base_genome.memory_decay:.2f}"
    )

    return archive, ecosystem, evolution_engine


if __name__ == "__main__":

    # 创建示例文件
    sample_files = []
    for i in range(3):
        fname = f"/tmp/phase9_sample_{i}.txt"
        Path(fname).write_text(
            f"Attention collapse in transformer models. "
            f"KV cache optimization document {i}. "
            f"Scaling laws for large language models."
        )
        sample_files.append(fname)

    asyncio.run(phase9_archive_main(sample_files))
