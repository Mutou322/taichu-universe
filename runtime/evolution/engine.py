"""GEP 进化引擎 — 沙盒实验、并行世代运行和最优 genome 采纳。"""

# runtime/evolution/engine.py

import asyncio
import logging
from typing import Any

from runtime.evolution.fitness import FitnessEvaluator
from runtime.evolution.mutation import GenomeMutator
from runtime.evolution.sandbox import SandboxRuntime

logger = logging.getLogger(__name__)


class EvolutionEngine:
    """基因表达式编程引擎：变异 -> 沙盒测试 -> 评估 -> 选优 -> 应用到生产。"""

    def __init__(self, runtime_graph: Any, base_genome: Any, parallelism: int = 4) -> None:
        self.runtime_graph = runtime_graph
        self.base_genome = base_genome
        self.parallelism = parallelism
        self.fitness_evaluator = FitnessEvaluator()
        self.mutator = GenomeMutator()

    async def run_sandbox_experiment(self, genome: Any) -> dict[str, Any]:
        sandbox = SandboxRuntime(self.runtime_graph, genome)
        results = await sandbox.run_test()
        fitness = self.fitness_evaluator.evaluate(results)

        return {
            "genome": genome,
            "results": results,
            "fitness": fitness,
        }

    async def run_parallel_generation(self, generation_size: int = 6) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """
        Week 2 & Week 3: 并行多 sandbox + metrics emit for Nebula UI
        """
        genomes = [self.mutator.mutate(self.base_genome) for _ in range(generation_size)]

        tasks = [asyncio.create_task(self.run_sandbox_experiment(g)) for g in genomes]
        results = await asyncio.gather(*tasks)

        # 按 fitness 降序
        results.sort(key=lambda r: r["fitness"], reverse=True)
        best_result = results[0]

        # 更新 base genome 为当前最优
        self.base_genome = best_result["genome"]

        # Emit metrics for Nebula UI
        from runtime.metrics.metrics_bus import metrics_bus
        from runtime.metrics.models import MetricEvent

        for r in results:
            event = MetricEvent(
                name="gep_sandbox_fitness",
                value=r["fitness"],
                tags={
                    "vector_top_k": r["genome"].vector_top_k,
                    "graph_depth": r["genome"].graph_depth,
                    "rerank_weight": r["genome"].rerank_weight,
                    "memory_decay": r["genome"].memory_decay,
                    "agent": getattr(self, "_agent_id", "single"),
                },
            )
            await metrics_bus.emit_async(event.name, event)

            from runtime.events.bus import bus

            bus.emit_async(
                "gep_sandbox_fitness",
                {
                    "fitness": r["fitness"],
                    "genome": {
                        "vector_top_k": r["genome"].vector_top_k,
                        "graph_depth": r["genome"].graph_depth,
                        "rerank_weight": r["genome"].rerank_weight,
                        "memory_decay": r["genome"].memory_decay,
                        "agent": getattr(self, "_agent_id", "single"),
                    },
                },
            )

        return results, best_result

    async def adopt_best_genome(self) -> Any:
        """
        Week 5: 将最优 genome 应用到正式 Runtime。
        红线：不改知识库，只改 Runtime 策略。
        """
        from runtime.runtime_config import runtime_config

        runtime_config.vector_top_k = self.base_genome.vector_top_k
        runtime_config.graph_depth = self.base_genome.graph_depth
        runtime_config.rerank_weight = self.base_genome.rerank_weight
        runtime_config.memory_decay = self.base_genome.memory_decay

        logger.info("[GEP] Adopted best genome to production Runtime:")
        logger.info("  vector_top_k=%s", runtime_config.vector_top_k)
        logger.info("  graph_depth=%s", runtime_config.graph_depth)
        logger.info("  rerank_weight=%s", runtime_config.rerank_weight)
        logger.info("  memory_decay=%s", runtime_config.memory_decay)

        return runtime_config
