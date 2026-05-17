"""工作流规划阶段的指标上报工具。"""

# runtime/planning/planning_metrics.py

from typing import Any

from runtime.metrics.metrics_bus import metrics_bus
from runtime.metrics.models import MetricEvent


async def emit_workflow_metrics(workflow: Any) -> None:

    total_nodes = len(workflow.nodes)

    completed = sum(1 for n in workflow.nodes.values() if n.completed)

    event = MetricEvent(
        name="workflow_progress",
        value=completed,
        tags={
            "total_nodes": total_nodes,
        },
    )

    await metrics_bus.emit_async(event.name, event)
