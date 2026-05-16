# runtime/semantic/semantic_metrics.py

from runtime.metrics.metrics_bus import metrics_bus
from runtime.metrics.models import MetricEvent


async def emit_semantic_metrics(memory):
    snapshot = memory.snapshot()
    total_concepts = len(snapshot)
    total_activation = sum(x["activation"] for x in snapshot.values())

    event = MetricEvent(
        name="semantic_field",
        value=total_activation,
        tags={"concepts": total_concepts},
    )
    await metrics_bus.emit(event.name, event)
