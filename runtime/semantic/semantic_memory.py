"""语义记忆 — 线程安全的概念激活值存储，支持累积激活与快照"""

import threading
import time


class SemanticMemory:
    """线程安全的概念-激活值映射表"""

    def __init__(self) -> None:
        self.nodes: dict[str, dict] = {}
        self._lock = threading.Lock()

    def activate(self, concept: str, strength: float = 1.0, source: str | None = None) -> None:
        """累积激活概念（若不存在则自动创建），记录触发来源与更新时间"""
        with self._lock:
            if concept not in self.nodes:
                self.nodes[concept] = {
                    "activation": 0.0,
                    "sources": set(),
                    "last_update": time.time(),
                }

            node = self.nodes[concept]
            node["activation"] += strength
            if source:
                node["sources"].add(source)
            node["last_update"] = time.time()

    def get_activation(self, concept: str) -> float:
        if concept not in self.nodes:
            return 0.0
        return self.nodes[concept]["activation"]

    def snapshot(self) -> dict[str, dict]:
        return self.nodes
