# runtime/evolution/genome.py

from dataclasses import dataclass


@dataclass
class Genome:
    vector_top_k: int = 8
    graph_depth: int = 2
    rerank_weight: float = 0.6
    memory_decay: float = 0.95

    def clone(self):
        return Genome(
            vector_top_k=self.vector_top_k,
            graph_depth=self.graph_depth,
            rerank_weight=self.rerank_weight,
            memory_decay=self.memory_decay,
        )

    def adjust(self, task_type, reward):
        pass
