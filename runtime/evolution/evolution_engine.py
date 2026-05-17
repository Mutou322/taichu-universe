"""轻量进化引擎 — 单世代变异-评估-选优循环。"""

# runtime/evolution/evolution_engine.py

import asyncio
from copy import deepcopy
from typing import Any

from runtime.evolution.fitness import FitnessEvaluator
from runtime.evolution.mutation import genome_mutator
from runtime.evolution.sandbox import run_sandbox


class EvolutionEngine:
    """每代从 base genome 变异出种群，沙盒评估后选出最优作为下一代的 base。"""

    POPULATION_SIZE = 6

    def __init__(self, base_genome: Any, metrics_bus: Any, gbrain: Any) -> None:

        self.base_genome = deepcopy(base_genome)
        self.metrics_bus = metrics_bus
        self.gbrain = gbrain
        self.generation = 0

    async def run_generation(self, agents: Any, gbrain_output: Any = None) -> tuple[Any, list[float]]:
        """执行一代进化：变异 -> 并行沙盒 -> 评估 fitness -> 选最优 -> 更新 base genome。"""
        genomes = [genome_mutator.mutate(self.base_genome) for _ in range(self.POPULATION_SIZE)]

        sandbox_results = await asyncio.gather(*[run_sandbox(genome, agents, gbrain_output) for genome in genomes])

        fitness_results = [FitnessEvaluator.evaluate(res) for res in sandbox_results]

        best_idx = max(
            range(len(fitness_results)),
            key=lambda i: fitness_results[i],
        )

        self.base_genome = sandbox_results[best_idx]["genome"]

        self.metrics_bus.emit(
            "evolution",
            {
                "generation": self.generation,
                "fitness_results": fitness_results,
                "best_genome": self.base_genome,
            },
        )

        self.generation += 1

        return self.base_genome, fitness_results
