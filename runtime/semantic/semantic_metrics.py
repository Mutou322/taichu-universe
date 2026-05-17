"""语义指标 — 将语义场的激活状态推送到 metrics_bus"""

from typing import Any

from runtime.metrics.metrics_bus import metrics_bus
from runtime.metrics.models import MetricEvent


async def emit_semantic_metrics(memory: Any) -> None:
    """汇总语义记忆快照中的概念总量和总激活值并上报指标"""
    snapshot = memory.snapshot()
    total_concepts = len(snapshot)
    total_activation = sum(x["activation"] for x in snapshot.values())

    event = MetricEvent(
        name="semantic_field",
        value=total_activation,
        tags={"concepts": total_concepts},
    )
    await metrics_bus.emit_async(event.name, event)
