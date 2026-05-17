"""Genome 随机变异器。"""

# runtime/evolution/mutation.py

import random

from runtime.evolution.genome import Genome


class GenomeMutator:
    """按 mutation_rate 对 genome 各参数随机扰动变异。"""

    DEFAULT_MUTATION_RATE = 0.3
    RERANK_WEIGHT_DELTA = 0.1
    MEMORY_DECAY_DELTA = 0.05

    def mutate(self, genome: Genome, mutation_rate: float = DEFAULT_MUTATION_RATE) -> Genome:
        """
        随机变异 genome 参数。

        mutation_rate: 每个参数被变异的概率。
        """
        new_genome = genome.clone()

        if random.random() < mutation_rate:
            new_genome.vector_top_k = max(1, new_genome.vector_top_k + random.choice([-1, 1]))

        if random.random() < mutation_rate:
            new_genome.graph_depth = max(1, new_genome.graph_depth + random.choice([-1, 1]))

        if random.random() < mutation_rate:
            new_genome.rerank_weight = min(
                max(
                    0.0, new_genome.rerank_weight + random.uniform(-self.RERANK_WEIGHT_DELTA, self.RERANK_WEIGHT_DELTA)
                ),
                1.0,
            )

        if random.random() < mutation_rate:
            new_genome.memory_decay = min(
                max(0.5, new_genome.memory_decay + random.uniform(-self.MEMORY_DECAY_DELTA, self.MEMORY_DECAY_DELTA)),
                1.0,
            )

        return new_genome


genome_mutator = GenomeMutator()
