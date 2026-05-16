# runtime/gbrain/gravity_metrics.py

import asyncio

from runtime.metrics.metrics_bus import metrics_bus
from runtime.metrics.models import MetricEvent


async def emit_gravity_metrics(gravity_updates: dict):
    """把 gravity 更新推送到 metrics_bus"""
    if not gravity_updates:
        return

    total_gravity = sum(gravity_updates.values())
    avg_gravity = total_gravity / max(len(gravity_updates), 1)

    event = MetricEvent(
        name="semantic_gravity",
        value=avg_gravity,
        tags={"node_count": len(gravity_updates)},
    )

    await metrics_bus.emit(event.name, event)

    # 同时推送到 EventBus（用于 WebSocket 广播）
    from runtime.events.bus import bus

    bus.emit_async(
        "semantic_gravity",
        {
            "avg_gravity": avg_gravity,
            "node_count": len(gravity_updates),
        },
    )
