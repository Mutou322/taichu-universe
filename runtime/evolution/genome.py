"""Genome 基因型数据结构，编码 Runtime 可调参数。"""

# runtime/evolution/genome.py

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Genome:
    """基因型：vector_top_k、graph_depth、rerank_weight、memory_decay。"""

    vector_top_k: int = 8
    graph_depth: int = 2
    rerank_weight: float = 0.6
    memory_decay: float = 0.95

    def clone(self) -> "Genome":
        return Genome(
            vector_top_k=self.vector_top_k,
            graph_depth=self.graph_depth,
            rerank_weight=self.rerank_weight,
            memory_decay=self.memory_decay,
        )

    def adjust(self, task_type: str, reward: float) -> None:
        """Adjust genome parameters based on task feedback.

        This is a placeholder for future reinforcement learning on genome
        parameters. Currently a no-op — stores the feedback for later use.
        """
        self._last_task_type = task_type
        self._last_reward = reward
        logger.debug(
            "Genome.adjust() called with task_type=%r, reward=%r (no-op placeholder)",
            task_type,
            reward,
        )
