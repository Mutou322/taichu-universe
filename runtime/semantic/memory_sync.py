# runtime/semantic/memory_sync.py


class MemorySynchronizer:

    def __init__(self, memory):
        self.memory = memory

    def top_active_concepts(self, top_k=10):
        snapshot = self.memory.snapshot()
        ranked = sorted(
            snapshot.items(),
            key=lambda x: x[1]["activation"],
            reverse=True,
        )
        return ranked[:top_k]
