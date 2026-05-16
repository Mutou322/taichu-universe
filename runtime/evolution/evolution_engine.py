# runtime/evolution/evolution_engine.py

import asyncio
from copy import deepcopy

from runtime.evolution.fitness import FitnessEvaluator
from runtime.evolution.mutation import genome_mutator
from runtime.evolution.sandbox import run_sandbox


class EvolutionEngine:

    def __init__(self, base_genome, metrics_bus, gbrain):

        self.base_genome = deepcopy(base_genome)
        self.metrics_bus = metrics_bus
        self.gbrain = gbrain
        self.generation = 0

    async def run_generation(self, agents, gbrain_output=None):

        genomes = [genome_mutator.mutate(self.base_genome) for _ in range(6)]

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
