# runtime/gbrain/cluster_metrics.py

import asyncio

from runtime.metrics.metrics_bus import metrics_bus
from runtime.metrics.models import MetricEvent


async def emit_cluster_metrics(clusters):
    if not clusters:
        return

    cluster_count = len(clusters)
    largest_cluster = max((len(v) for v in clusters.values()), default=0)

    event = MetricEvent(
        name="graph_clusters",
        value=largest_cluster,
        tags={"cluster_count": cluster_count},
    )

    await metrics_bus.emit(event.name, event)

    # 同步推送到 EventBus（用于 WS 广播）
    from runtime.events.bus import bus

    bus.emit_async(
        "graph_clusters",
        {
            "clusters": {k: v for k, v in clusters.items()},
            "cluster_count": cluster_count,
            "largest_size": largest_cluster,
        },
    )
