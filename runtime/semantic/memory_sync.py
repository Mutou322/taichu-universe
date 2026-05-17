"""内存同步器 — 从 SemanticMemory 快照中提取活跃概念排行"""

from typing import Any


class MemorySynchronizer:
    """从语义记忆中提取 Top-K 活跃概念的同步器"""

    def __init__(self, memory: Any) -> None:
        self.memory = memory

    def top_active_concepts(self, top_k: int = 10) -> list[tuple[str, dict]]:
        snapshot = self.memory.snapshot()
        ranked = sorted(
            snapshot.items(),
            key=lambda x: x[1]["activation"],
            reverse=True,
        )
        return ranked[:top_k]
