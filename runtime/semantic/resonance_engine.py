"""共鸣引擎 — 基于概念关联关系传播激活能量"""

from typing import Any

# ── 共鸣传播系数 ──
PROPAGATION_FACTOR = 0.2


class ResonanceEngine:
    """将概念的激活值按关联关系传播给邻居节点"""

    def __init__(self, memory: Any) -> None:
        self.memory = memory
        self.relations = {
            # TODO: 从 knowledge/relations/ 加载真实关系数据
            # 当前为演示占位，Phase 3 后从图谱自动生成
            "Transformer": ["Attention", "KV Cache"],
            "Attention": ["FlashAttention"],
            "LLM": ["GPT", "Claude"],
        }

    def propagate(self) -> None:
        updates = []
        snapshot = self.memory.snapshot()

        for concept, data in snapshot.items():
            activation = data["activation"]
            related = self.relations.get(concept, [])
            for r in related:
                propagated = activation * PROPAGATION_FACTOR
                updates.append((r, propagated))

        for concept, value in updates:
            self.memory.activate(concept, strength=value, source="resonance")
