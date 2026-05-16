# runtime/semantic/resonance_engine.py


class ResonanceEngine:

    def __init__(self, memory):
        self.memory = memory
        self.relations = {
            # TODO: 从 knowledge/relations/ 加载真实关系数据
            # 当前为演示占位，Phase 3 后从图谱自动生成
            "Transformer": ["Attention", "KV Cache"],
            "Attention": ["FlashAttention"],
            "LLM": ["GPT", "Claude"],
        }

    def propagate(self):
        updates = []
        snapshot = self.memory.snapshot()

        for concept, data in snapshot.items():
            activation = data["activation"]
            related = self.relations.get(concept, [])
            for r in related:
                propagated = activation * 0.2
                updates.append((r, propagated))

        for concept, value in updates:
            self.memory.activate(concept, strength=value, source="resonance")
