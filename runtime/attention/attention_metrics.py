# runtime/attention/attention_metrics.py


class AttentionMetrics:

    def __init__(self, metrics_bus, attention_history):

        self.metrics_bus = metrics_bus
        self.attention_history = attention_history

    async def emit(self, attention_map):

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
