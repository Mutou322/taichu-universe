"""Emits attention-related metrics to the metrics bus and history."""

from typing import Any


class AttentionMetrics:
    """Collects attention snapshots and emits them to the metrics bus."""

    def __init__(self, metrics_bus: Any, attention_history: Any) -> None:

        self.metrics_bus = metrics_bus
        self.attention_history = attention_history

    async def emit(self, attention_map: Any) -> None:

        self.attention_history.add_snapshot(attention_map)

        data = {}

        for node_id, agents in attention_map.all_weights().items():

            data[node_id] = dict(agents)

        await self.metrics_bus.emit_async(
            "attention_map",
            {
                "current": data,
                "history": self.attention_history.get_history(),
            },
        )
