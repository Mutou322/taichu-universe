# runtime/gbrain/ontology_metrics.py

import asyncio

from runtime.metrics.metrics_bus import metrics_bus
from runtime.metrics.models import MetricEvent


async def emit_ontology_metrics(ontology):
    if not ontology:
        return

    core_nodes = sum(len(v["core"]) for v in ontology.values())
    secondary_nodes = sum(len(v["secondary"]) for v in ontology.values())
    total_nodes = core_nodes + secondary_nodes

    event = MetricEvent(
        name="ontology_metrics",
        value=total_nodes,
        tags={
            "core_nodes": core_nodes,
            "secondary_nodes": secondary_nodes,
            "clusters": len(ontology),
        },
    )

    await metrics_bus.emit(event.name, event)

    # 同步推送到 EventBus（用于 WS 广播）
    from runtime.events.bus import bus

    bus.emit_async(
        "ontology_metrics",
        {
            "clusters": ontology,
            "core_nodes": core_nodes,
            "secondary_nodes": secondary_nodes,
            "total_clusters": len(ontology),
        },
    )
